`timescale 1ns / 1ps

module axis_frame_decimator #(
    parameter integer DATA_WIDTH = 24,
    parameter integer USER_WIDTH = 1
) (
    input  wire                     aclk,
    input  wire                     aresetn,

    input  wire [15:0]              decimation_factor,
    input  wire                     enable,
    output reg  [31:0]              accepted_frames,
    output reg  [31:0]              dropped_frames,

    input  wire [DATA_WIDTH-1:0]    s_axis_tdata,
    input  wire [USER_WIDTH-1:0]    s_axis_tuser,
    input  wire                     s_axis_tvalid,
    output wire                     s_axis_tready,
    input  wire                     s_axis_tlast,

    output wire [DATA_WIDTH-1:0]    m_axis_tdata,
    output wire [USER_WIDTH-1:0]    m_axis_tuser,
    output wire                     m_axis_tvalid,
    input  wire                     m_axis_tready,
    output wire                     m_axis_tlast
);

    localparam DROP  = 1'b0;
    localparam PASS  = 1'b1;

    reg        frame_state;
    reg [15:0] frame_index;
    reg        in_frame;

    wire sof = s_axis_tvalid && s_axis_tready && s_axis_tuser[0];
    wire xfer = s_axis_tvalid && s_axis_tready;
    wire [15:0] factor = (decimation_factor == 16'd0) ? 16'd1 : decimation_factor;
    wire pass_sample = enable && (frame_state == PASS);

    assign s_axis_tready = pass_sample ? m_axis_tready : 1'b1;
    assign m_axis_tdata  = s_axis_tdata;
    assign m_axis_tuser  = s_axis_tuser;
    assign m_axis_tlast  = s_axis_tlast;
    assign m_axis_tvalid = s_axis_tvalid && pass_sample;

    always @(posedge aclk) begin
        if (!aresetn) begin
            frame_state     <= DROP;
            frame_index     <= 16'd0;
            in_frame        <= 1'b0;
            accepted_frames <= 32'd0;
            dropped_frames  <= 32'd0;
        end else begin
            if (!enable) begin
                frame_state <= DROP;
                frame_index <= 16'd0;
                in_frame    <= 1'b0;
            end else if (sof) begin
                in_frame <= 1'b1;
                if (frame_index == 16'd0) begin
                    frame_state     <= PASS;
                    accepted_frames <= accepted_frames + 32'd1;
                end else begin
                    frame_state    <= DROP;
                    dropped_frames <= dropped_frames + 32'd1;
                end

                if (frame_index >= factor - 16'd1) begin
                    frame_index <= 16'd0;
                end else begin
                    frame_index <= frame_index + 16'd1;
                end
            end else if (xfer && s_axis_tlast && in_frame) begin
                in_frame <= 1'b1;
            end
        end
    end

endmodule


`timescale 1ns / 1ps

module mcvr_registers #(
    parameter integer C_S_AXI_DATA_WIDTH = 32,
    parameter integer C_S_AXI_ADDR_WIDTH = 8
) (
    input  wire                             s_axi_aclk,
    input  wire                             s_axi_aresetn,
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]    s_axi_awaddr,
    input  wire                             s_axi_awvalid,
    output reg                              s_axi_awready,
    input  wire [C_S_AXI_DATA_WIDTH-1:0]    s_axi_wdata,
    input  wire [(C_S_AXI_DATA_WIDTH/8)-1:0] s_axi_wstrb,
    input  wire                             s_axi_wvalid,
    output reg                              s_axi_wready,
    output reg  [1:0]                       s_axi_bresp,
    output reg                              s_axi_bvalid,
    input  wire                             s_axi_bready,
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]    s_axi_araddr,
    input  wire                             s_axi_arvalid,
    output reg                              s_axi_arready,
    output reg  [C_S_AXI_DATA_WIDTH-1:0]    s_axi_rdata,
    output reg  [1:0]                       s_axi_rresp,
    output reg                              s_axi_rvalid,
    input  wire                             s_axi_rready,

    output wire                             enable,
    output wire                             soft_reset,
    output wire [15:0]                      decimation_factor,
    output wire [31:0]                      width,
    output wire [31:0]                      height,
    output wire [31:0]                      frame_bytes,
    input  wire [31:0]                      frame_count0,
    input  wire [31:0]                      frame_count1,
    input  wire [31:0]                      frame_count2,
    input  wire [31:0]                      frame_count3
);

    reg [31:0] control_reg;
    reg [31:0] decimation_reg;
    reg [31:0] width_reg;
    reg [31:0] height_reg;
    reg [31:0] frame_bytes_reg;
    reg [C_S_AXI_ADDR_WIDTH-1:0] awaddr_latched;
    reg [C_S_AXI_ADDR_WIDTH-1:0] araddr_latched;

    assign enable            = control_reg[0];
    assign soft_reset        = control_reg[1];
    assign decimation_factor = decimation_reg[15:0];
    assign width             = width_reg;
    assign height            = height_reg;
    assign frame_bytes       = frame_bytes_reg;

    wire write_fire = s_axi_awready && s_axi_awvalid && s_axi_wready && s_axi_wvalid;
    wire read_fire  = s_axi_arready && s_axi_arvalid;

    integer i;

    always @(posedge s_axi_aclk) begin
        if (!s_axi_aresetn) begin
            control_reg     <= 32'h0000_0000;
            decimation_reg  <= 32'h0000_0003;
            width_reg       <= 32'd1920;
            height_reg      <= 32'd1536;
            frame_bytes_reg <= 32'd8847360;
            s_axi_awready   <= 1'b0;
            s_axi_wready    <= 1'b0;
            s_axi_bresp     <= 2'b00;
            s_axi_bvalid    <= 1'b0;
            s_axi_arready   <= 1'b0;
            s_axi_rdata     <= 32'd0;
            s_axi_rresp     <= 2'b00;
            s_axi_rvalid    <= 1'b0;
            awaddr_latched  <= {C_S_AXI_ADDR_WIDTH{1'b0}};
            araddr_latched  <= {C_S_AXI_ADDR_WIDTH{1'b0}};
        end else begin
            s_axi_awready <= !s_axi_awready && s_axi_awvalid && s_axi_wvalid;
            s_axi_wready  <= !s_axi_wready && s_axi_wvalid && s_axi_awvalid;
            s_axi_arready <= !s_axi_arready && s_axi_arvalid && !s_axi_rvalid;

            if (s_axi_awready && s_axi_awvalid) begin
                awaddr_latched <= s_axi_awaddr;
            end

            if (write_fire) begin
                for (i = 0; i < C_S_AXI_DATA_WIDTH/8; i = i + 1) begin
                    if (s_axi_wstrb[i]) begin
                        case (awaddr_latched[7:0])
                            8'h00: control_reg[(i*8) +: 8]     <= s_axi_wdata[(i*8) +: 8];
                            8'h04: decimation_reg[(i*8) +: 8]  <= s_axi_wdata[(i*8) +: 8];
                            8'h08: width_reg[(i*8) +: 8]       <= s_axi_wdata[(i*8) +: 8];
                            8'h0c: height_reg[(i*8) +: 8]      <= s_axi_wdata[(i*8) +: 8];
                            8'h10: frame_bytes_reg[(i*8) +: 8] <= s_axi_wdata[(i*8) +: 8];
                            default: ;
                        endcase
                    end
                end
                s_axi_bvalid <= 1'b1;
                s_axi_bresp  <= 2'b00;
            end else if (s_axi_bvalid && s_axi_bready) begin
                s_axi_bvalid <= 1'b0;
            end

            if (read_fire) begin
                araddr_latched <= s_axi_araddr;
                s_axi_rvalid   <= 1'b1;
                s_axi_rresp    <= 2'b00;
                case (s_axi_araddr[7:0])
                    8'h00: s_axi_rdata <= control_reg;
                    8'h04: s_axi_rdata <= decimation_reg;
                    8'h08: s_axi_rdata <= width_reg;
                    8'h0c: s_axi_rdata <= height_reg;
                    8'h10: s_axi_rdata <= frame_bytes_reg;
                    8'h20: s_axi_rdata <= {31'd0, control_reg[0]};
                    8'h24: s_axi_rdata <= frame_count0;
                    8'h28: s_axi_rdata <= frame_count1;
                    8'h2c: s_axi_rdata <= frame_count2;
                    8'h30: s_axi_rdata <= frame_count3;
                    default: s_axi_rdata <= 32'd0;
                endcase
            end else if (s_axi_rvalid && s_axi_rready) begin
                s_axi_rvalid <= 1'b0;
            end
        end
    end

endmodule


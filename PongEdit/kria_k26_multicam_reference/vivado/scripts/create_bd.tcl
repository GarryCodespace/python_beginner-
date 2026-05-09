create_bd_design kria_multicam_bd

proc ip_available {vlnv} {
    return [expr {[llength [get_ipdefs -all $vlnv]] > 0}]
}

proc create_checked_cell {name vlnv} {
    if {![ip_available $vlnv]} {
        puts "WARNING: IP $vlnv is not available in this Vivado installation."
        puts "         Install/enable the IP or replace $name with the local equivalent."
        return ""
    }
    return [create_bd_cell -type ip -vlnv $vlnv $name]
}

set ps [create_checked_cell zynq_ultra_ps_e_0 xilinx.com:ip:zynq_ultra_ps_e:*]
if {$ps ne ""} {
    set_property -dict [list CONFIG.PSU__USE__M_AXI_GP0 {1} CONFIG.PSU__USE__S_AXI_GP0 {1} CONFIG.PSU__USE__S_AXI_GP1 {1}] $ps
}

set rst [create_checked_cell rst_ps8_0_99M xilinx.com:ip:proc_sys_reset:*]
set axi_ctrl [create_checked_cell axi_ctrl_smc xilinx.com:ip:smartconnect:*]
set axi_mem  [create_checked_cell axi_mem_smc xilinx.com:ip:smartconnect:*]

set xdma [create_checked_cell xdma_0 xilinx.com:ip:xdma:*]
if {$xdma ne ""} {
    set_property -dict [list \
        CONFIG.mode_selection {Advanced} \
        CONFIG.pl_link_cap_max_link_width {X4} \
        CONFIG.pl_link_cap_max_link_speed {8.0_GT/s} \
        CONFIG.axisten_freq {250} \
        CONFIG.dma_intf {AXI_MM} \
        CONFIG.pf0_device_id {903F} \
    ] $xdma
}

create_bd_cell -type module -reference mcvr_registers mcvr_registers_0

for {set i 0} {$i < 4} {incr i} {
    set tpg [create_checked_cell v_tpg_$i xilinx.com:ip:v_tpg:*]
    set vdma [create_checked_cell axi_vdma_$i xilinx.com:ip:axi_vdma:*]
    create_bd_cell -type module -reference axis_frame_decimator axis_frame_decimator_$i

    if {$tpg ne ""} {
        set_property -dict [list \
            CONFIG.SAMPLES_PER_CLOCK {1} \
            CONFIG.MAX_COLS {1920} \
            CONFIG.MAX_ROWS {1536} \
            CONFIG.VIDEO_FORMAT {2} \
        ] $tpg
    }

    if {$vdma ne ""} {
        set_property -dict [list \
            CONFIG.c_include_mm2s {0} \
            CONFIG.c_include_s2mm {1} \
            CONFIG.c_s2mm_genlock_mode {0} \
            CONFIG.c_s2mm_linebuffer_depth {4096} \
            CONFIG.c_num_fstores {3} \
            CONFIG.c_m_axis_mm2s_tdata_width {32} \
            CONFIG.c_s_axis_s2mm_tdata_width {32} \
        ] $vdma
    }

    if {$tpg ne "" && $vdma ne ""} {
        connect_bd_intf_net [get_bd_intf_pins v_tpg_$i/m_axis_video] [get_bd_intf_pins axis_frame_decimator_$i/s_axis]
        connect_bd_intf_net [get_bd_intf_pins axis_frame_decimator_$i/m_axis] [get_bd_intf_pins axi_vdma_$i/S_AXIS_S2MM]
    }

    connect_bd_net [get_bd_pins mcvr_registers_0/enable] [get_bd_pins axis_frame_decimator_$i/enable]
    connect_bd_net [get_bd_pins mcvr_registers_0/decimation_factor] [get_bd_pins axis_frame_decimator_$i/decimation_factor]
}

# Addressing, clocks, resets, and DDR/HP port connections are intentionally left
# visible for the integrator. They depend on final PS configuration, selected
# carrier board, and whether frames are written through HP/HPC ports or routed
# through an alternate memory subsystem.
#
# Recommended manual completion in IP Integrator:
# 1. Connect PS pl_clk0 to AXI-Lite, TPG, decimator, VDMA lite, and reset blocks.
# 2. Connect VDMA S2MM memory-mapped masters to PS DDR through HP/HPC ports.
# 3. Connect XDMA AXI master to the DDR address range used for frame buffers.
# 4. Map mcvr_registers_0 and VDMA register spaces into the PS AXI-Lite map.
# 5. Map XDMA BAR0 to AXI-Lite control/status access if host register access is required.
# 6. Validate design and assign addresses.

save_bd_design


set script_dir [file dirname [file normalize [info script]]]
set root_dir   [file normalize [file join $script_dir ../..]]
set proj_dir   [file join $root_dir build/vivado]
set proj_name  kria_k26_multicam_ref

set part_name [expr {[info exists ::env(KRIA_K26_PART)] ? $::env(KRIA_K26_PART) : "xck26-sfvc784-2LV-c"}]

file mkdir $proj_dir
create_project $proj_name $proj_dir -part $part_name -force

set_property target_language Verilog [current_project]
set_property default_lib xil_defaultlib [current_project]

add_files -norecurse [glob -nocomplain [file join $root_dir vivado/rtl/*.v]]
add_files -fileset constrs_1 -norecurse [file join $root_dir vivado/constraints/kria_k26_multicam.xdc]

source [file join $script_dir create_bd.tcl]

make_wrapper -files [get_files [file join $proj_dir $proj_name.srcs/sources_1/bd/kria_multicam_bd/kria_multicam_bd.bd]] -top
add_files -norecurse [file join $proj_dir $proj_name.gen/sources_1/bd/kria_multicam_bd/hdl/kria_multicam_bd_wrapper.v]
set_property top kria_multicam_bd_wrapper [current_fileset]

puts "Created $proj_name in $proj_dir"
puts "Next: validate_bd_design, generate_target all, synth_design, impl_design, write_hw_platform"


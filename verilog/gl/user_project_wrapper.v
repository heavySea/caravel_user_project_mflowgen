/*
###############################################################
#  Generated by:      Cadence Innovus 17.11-s080_1
#  OS:                Linux x86_64(Host ID localhost.localdomain)
#  Generated on:      Tue Jun 22 11:43:10 2021
#  Design:            user_project_wrapper
###############################################################
*/
module user_project_wrapper (
	wb_clk_i, 
	wb_rst_i, 
	wbs_stb_i, 
	wbs_cyc_i, 
	wbs_we_i, 
	wbs_sel_i, 
	wbs_dat_i, 
	wbs_adr_i, 
	wbs_ack_o, 
	wbs_dat_o, 
	la_data_in, 
	la_data_out, 
	la_oenb, 
	io_in, 
	io_out, 
	io_oeb, 
	analog_io, 
	user_clock2, 
	user_irq, 
	vssa2, 
	vssa1, 
	vssd2, 
	vssd1, 
	vdda2, 
	vdda1, 
	vccd2, 
	vccd1);
   input wb_clk_i;
   input wb_rst_i;
   input wbs_stb_i;
   input wbs_cyc_i;
   input wbs_we_i;
   input [3:0] wbs_sel_i;
   input [31:0] wbs_dat_i;
   input [31:0] wbs_adr_i;
   output wbs_ack_o;
   output [31:0] wbs_dat_o;
   input [127:0] la_data_in;
   output [127:0] la_data_out;
   input [127:0] la_oenb;
   input [37:0] io_in;
   output [37:0] io_out;
   output [37:0] io_oeb;
   inout [28:0] analog_io;
   input user_clock2;
   output [2:0] user_irq;
   inout vssa2;
   inout vssa1;
   inout vssd2;
   inout vssd1;
   inout vdda2;
   inout vdda1;
   inout vccd2;
   inout vccd1;

   // Internal wires

   // Module instantiations
   user_proj_example mprj (
	.wb_clk_i(wb_clk_i),
	.wb_rst_i(wb_rst_i),
	.wbs_stb_i(wbs_stb_i),
	.wbs_cyc_i(wbs_cyc_i),
	.wbs_we_i(wbs_we_i),
	.wbs_sel_i(wbs_sel_i),
	.wbs_dat_i(wbs_dat_i),
	.wbs_adr_i(wbs_adr_i),
	.wbs_ack_o(wbs_ack_o),
	.wbs_dat_o(wbs_dat_o),
	.la_data_in(la_data_in),
	.la_data_out(la_data_out),
	.la_oenb(la_oenb),
	.io_in(io_in),
	.io_out(io_out),
	.io_oeb(io_oeb),
	.irq(user_irq), 
	.vssd1(vssd1), 
	.vccd1(vccd1));
endmodule


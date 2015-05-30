.model tiny
.data
Address	db	'C:\MASM611\BIN\Lab4\data.txt',0
Handle	dw	?
data	db	'AYUSH SHARMA',0dh,0Ah,'2013A7PS083G',0Dh,0Ah,
		'AYUSH SHARMA',0dh,0Ah,'2013A7PS083G',0Dh,0Ah
.code
.startup
	mov	ah,3Ch
	mov	dx,offset Address
	mov	cl,01h
	int	21h
	mov	Handle,AX
	mov	ah,40H
	mov	bx,Handle
	mov	cx,56
	mov	dx,offset data
	int	21h
	mov	ah,3Eh
	int	21h
.exit
end

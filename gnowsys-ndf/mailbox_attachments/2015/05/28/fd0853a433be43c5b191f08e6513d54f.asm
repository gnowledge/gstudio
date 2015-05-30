.model tiny
.data
ADDRESS	db	'C:\MASM611\BIN\Lab4\data.txt',0
Handle	dw	?
Data	db	'AH7-111',0Dh,0Ah
.code
.startup
	mov	ah,3Dh		;To open the file
	lea	dx,ADDRESS
	mov	al,01h
	int	21h
	mov	Handle,AX
	mov	ah,42h		;TO reach the end
	mov	al,02h
	mov	cx,8000h
	mov	dx,0001h
	mov	bx,Handle
	int	21h
	mov	ah,40h		;To write the data
	mov	bx,Handle
	mov	cx,09
	lea	dx,Data
	int	21h
	mov	ah,3Eh		;To close the file
	int	21h
.exit
end

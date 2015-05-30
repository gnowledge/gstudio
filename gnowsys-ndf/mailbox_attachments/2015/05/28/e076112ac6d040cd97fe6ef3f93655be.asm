.model tiny
.data
max		db	20
count	db	?
str1	db	21 DUP(0)
.code
.startup
	lea	dx,max
	mov ah,0Ah
	int 21h
	lea	si,str1
	mov	bl,count
	mov	bh,00
	add	si,bx
	mov cl,'$'
	mov [si],cl
	lea dx,str1
	mov	ah,09h
	int 21h
.exit
end
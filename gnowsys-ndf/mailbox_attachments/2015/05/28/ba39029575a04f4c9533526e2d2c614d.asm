.model tiny
.data
str1	db	'Enter the username$'
str2	db	'Enter the password$'
user	db	'Ayush'
pass    db	'akazuko'
maxuser	db	10
count1	db	?
userinp	db	11 DUP(0)
maxpass	db	8
count2	db	?
passinp	db	9 DUP(0)
wel		db	'Hello $'

.code
.startup
	lea	dx,str1
	mov	ah,09h
	int 21h
	mov	dl,0Dh
	mov	ah,02h
	int 21h
	lea	dx,maxuser
	mov	ah,0Ah
	int 21h
	mov	cl,count1
	mov ch,00h
	lea	si,user
	add	dx,02h
	mov bx,dx
x1:	mov al,[si]
	cmp	al,byte ptr[bx]
	jne	x2
	inc	bx
	inc si
	loop x1
	lea	dx,str2
	mov	ah,09h
	int 21h
	mov	dl,0Dh
	mov	ah,02h
	int 21h
	lea	dx,maxpass
	mov	ah,0Ah
	int 21h
	mov	cl,count2
	mov ch,00h
	lea	si,pass
	add	dx,02h
	mov bx,dx
x3:	mov al,[si]
	cmp	al,byte ptr[bx]
	jne	x2
	inc	bx
	inc si
	loop x3
	lea	dx,wel
	mov	ah,09h
	int 21h
	lea si,user
	mov cl,count1
	mov	ch,00h
	cld
x4:	lodsb
	mov dl,al
	mov ah,02h
	int 21h
	loop x4
x2:
.exit
end
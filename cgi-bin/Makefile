UPLOAD_DIR=/home/louis/public_html/downloads
BG=../images/bg.gif
TMP_DIR=/var/tmp

CPPFLAGS=-DTMP_DIR="\"${TMP_DIR}\"" -DUPLOAD_DIR="\"${UPLOAD_DIR}\"" -DBG="\"${BG}\""

CGIS=upload.cgi remove.cgi

all: ${CGIS} proccgi

proccgi: proccgi.c
	gcc ${CPPFLAGS} proccgi.c -o proccgi

upload.cgi: upload.c
	gcc ${CPPFLAGS} upload.c -o upload.cgi

remove.cgi: remove.c
	gcc ${CPPFLAGS} remove.c -o remove.cgi

dict.cgi: dict.c
	gcc -Bstatic dict.c -o dict.cgi -lcgi -lqdbm

clean:
	rm ${CGIS} proccgi


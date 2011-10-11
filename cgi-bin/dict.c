#include <hovel.h>
#include <cgi.h>
#include <stdio.h>
#include <string.h>

typedef union int_bytes {
	int num;
	struct {
		char w;
		char xyz[3];
	} ch;
} int_bytes_u;

int main(int argc, char * argv[])
{
	GDBM_FILE dbf;
	char * str;
	datum data, key;
	int i, j, ret;
	int_bytes_u idx = {0};

	cgi_init();
	cgi_process_form();


	dbf = gdbm_open("/student/stu3/87/cs/d8728095/local/share/dict/21index.gdbm", 0, GDBM_READER, 0, 0);
	if (dbf == 0) cgi_fatal("can't open database.");

	str = cgi_param("word");
	if (str == NULL || strlen(str) == 0) cgi_fatal("query string can't be null!");

	cgi_init_headers();

	key.dptr = str;
	key.dsize = strlen(str);

	data = gdbm_fetch(dbf, key);
	if (data.dptr == NULL) cgi_fatal("查無此字");

	for(i = 0; i < data.dsize; i += 3)
	{
		memcpy(idx.ch.xyz, data.dptr + i, 3);
		if (idx.num >= 0x800000) {
			idx.num -= 0x800000;
			printf("s");
		}
		printf("%d\n", idx.num);
	}

	gdbm_close(dbf);
	cgi_end();
}

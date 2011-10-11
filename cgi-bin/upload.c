#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <assert.h>

#define BUFSIZE 512

char file_name[256];

void cgi_error(char *err_msg)
{
	assert(err_msg);

	printf("<p>ERROR: %s</p>", err_msg);
	exit(0);
}

char *basename(char *name)
{
	char *ptr;

	assert(name);

	ptr = strrchr(name, '/');
	if (ptr)
		return ptr + 1;
	else
		return name;
}

void decode_header(char *header)
{
	char *tmp;
	char *str;
	int i, len;

	tmp = strrchr(header, '\"');
	if (*tmp == *(tmp - 1))
		cgi_error("NO FILE NAME!");
	*tmp = '\0';

	tmp = strrchr(header, '\"');
	str = tmp + 1;
	len = strlen(str);
	for (i = 0; i < len; i++)
	{
		if (str[i] == '\\') // Qoo: utf-8 ? //
			tmp = str + i;
	}
	tmp++;
	if (strlen(tmp) <= 0)
		cgi_error("can't get the file name");

	strcpy(file_name, UPLOAD_DIR);
	strcat(file_name, "/");
	strcat(file_name, tmp);
}

void append_file_name(char *append)
{
	char *ptr;

	assert(append);

	ptr = strrchr(file_name, '.');
	if (!ptr)
	{
		strcat(file_name, append);
	}
	else
	{
		memmove(ptr + strlen(append), ptr, strlen(ptr) + 1);
		strncpy(ptr, append, strlen(append));
	}
}

int main(void)
{
	char *tmp;
	char linebuf[BUFSIZE];
	char tempname[128] = TMP_DIR;
	char *boundary;
	char *contype;
	int match;
	int fd, i, ch;
	int filelen;
	extern int errno;
	struct stat statbuf;

#ifdef DEBUG
	int contlen;
#endif

	printf("Content-Type: text/html\n\n");
	printf("<html><head><meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\" /></head><body background=\"%s\">", BG);

	contype = getenv("CONTENT_TYPE");
	if (contype == NULL)
		cgi_error("Missing CONTENT_TYPE");

	/* split "Content-Type" and "boundary" field from "CONTENT_TYPE" */
	tmp = strchr(contype, ';');
	*tmp = '\0';
	tmp++;
	tmp = strchr(tmp, '=');
	tmp -= 3;
	strncpy(tmp, "\r\n--", 4);
	boundary = tmp;

#ifdef DEBUG
	if (strcmp(contype, "multipart/form-data"))
		cgi_error("Content-Type is not correct!");
	if (boundary == NULL)
		cgi_error("Something wrong with boundary");

	contlen = atoi(getenv("CONTENT_LENGTH"));
	if (contlen <= 0)
		cgi_error("The length of content is incorrect");
#endif
	/* starting read data from STDIN */

	/* first line is boundary we check if match */
	fgets(linebuf, BUFSIZE, stdin);
#ifdef DEBUG
	if (strncmp(boundary + 2, linebuf, strlen(boundary + 2)))
		cgi_error("boundary doesn't match");
#endif
	/* seconed line contain Content-Discription and filename */
	fgets(linebuf, BUFSIZE, stdin);
	decode_header(linebuf);

	/* third line is the uploaded file Content-Type */
	fgets(linebuf, BUFSIZE, stdin);
	/* forth line only has '\n' */
	fgets(linebuf, BUFSIZE, stdin);

	if (stat(file_name, &statbuf) == 0) 
	{
		append_file_name("~");
		if (stat(file_name, &statbuf) == 0)
		{
			cgi_error("相同檔名重複太多。");
		}
	}

	strcat(tempname, "/myweb_XXXXXX");
	fd = mkstemp(tempname);
	if (fd <= 0)
		cgi_error("file open error");

	filelen = 0;
	match = 0;
	i = 0;
	for (;;)
	{
		ch = getc(stdin);
		if (feof(stdin)) /* transmit not complete */
		{
			close(fd);
			strcpy(linebuf, file_name);
			append_file_name("[上傳不完整]");
			rename(linebuf, file_name);
			printf("<p>WARNING: %s</p>", "檔案上傳不完全，請重新上傳。");
			break;
		}
		if (match)
		{
			if (ch == boundary[match])
			{
				match++;
				if (boundary[match] == '\0')
					break;
			}
			else
			{
				write(fd, boundary, match);
				filelen += match;
				match = 0;
				ungetc(ch, stdin);
			}
		}
		else
		{
			if (ch == boundary[match])
			{
				match++;
				write(fd, linebuf, i);
				filelen += i;
				i = 0;
			}
			else
				linebuf[i++] = (char) ch;
			if (i == BUFSIZE)
			{
				write(fd, linebuf, i);
				filelen += i;
				i = 0;
			}
		}
	}
	write(fd, linebuf, i);
	filelen += i;
	fchmod(fd, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
	close(fd);

	/* assert(filelen > 0); */

	symlink(tempname, file_name);
	printf("<b>%s</b>", basename(file_name));
	printf(" ( %d bytes )<br><br>", filelen);
	printf(".... 上傳完成 <a href=download.cgi>");
	printf("回上一頁</a>");
	printf("</body></html>");
}

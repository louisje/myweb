#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <assert.h>

void cgi_error(char * err_msg)
{
	assert(err_msg);

	printf("Content-Type: text/plain\n\n");
	printf("ERROR: %s", err_msg);
	exit(1);
}

int main(void)
{
	char * buffer;
	char * content_length;
	char * ptr;
	char * tmp;
	char bodyname[256];
	char linkname[256];

	int contlen;
	int index;
	int ch;

	content_length = getenv("CONTENT_LENGTH");
	if (content_length == NULL)
		cgi_error("where is CONTENT_LENGTH ?");
	contlen = atoi(content_length);
	if (contlen <= 0)
		cgi_error("nothing i can do `contlen <= 0'");
	buffer = (char*)malloc(contlen + 1);
	if (buffer == NULL)
		cgi_error("MALLOC");

	printf("Content-Type: text/html\n\n");
	printf("<html><head>\n");
	printf("<meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\" />\n");
	printf("</head><body background=\"%s\">\n", BG);

	index = 0;
	tmp = buffer;
	for (;;)
	{ 
		for (;;)
		{
			ch = getchar();
			index++;
			if (index == contlen)
			{
				*(tmp++) = (char)ch;
				*(tmp++) = '\0';
				break;
			}
			else if (ch == '+')
			{
				*(tmp++) = ' ';
			}
			else if (ch == '%')
			{
				scanf("%2x", &ch);
				index += 2;
				*(tmp++) = (char)ch;
				if (index == contlen)
				{
					*(tmp++) = '\0';
					break;
				}
			}
			else if (ch == '=')
			{
				*(tmp++) = '\0';
				ptr = tmp;
			}
			else if (ch == '&')
			{
				*(tmp++) = '\0';
				break;
			}
			else
				*(tmp++) = (char)ch;
		}
		printf("<b>%s</b><br>", ptr);

		strcpy(linkname, UPLOAD_DIR);
		strcat(linkname, "/");
		strcat(linkname, ptr);
		ch = readlink(linkname, bodyname, sizeof(bodyname));
		bodyname[ch] = '\0';
		remove(bodyname);
		unlink(linkname);

		if (index == contlen)
			break;
	}
	printf("<br>.... 刪除完成！ ");
	printf("<a href=download.cgi>");
	printf("回上一頁</a>");
	printf("</body></html>");
}

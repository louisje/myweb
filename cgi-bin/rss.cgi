#!/bin/bash

eval "`./proccgi $*`"

max_show="30"
torrent_directory="/home/louis/public_html/torrents"
upload_directory="/home/louis/public_html/downloads"
upload_url="http://xfire-a.no-ip.com/louis/downloads"

echo "Content-Type: application/rss+xml"
echo ""
echo "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
echo "<rss version=\"2.0\">"
echo "<channel>"
echo "<title>檔案櫃</title>"
echo "<link>http://202.5.224.193/louis/myweb/upload.htm</link>"
echo "<description>檔案櫃</description>"

cd "${upload_directory}"

/bin/ls -t1|{
total="0"
usage="0"
while read -r file; do
	if test -h "${file}" -a ! -d "${file}"; then
		target=`/bin/ls -o "./${file}"|sed 's/^.* -> \(.*\)$/\1/'`

		file_c=`echo ${file}|sed 's/%/%25/g'|sed 's/#/%23/g'|sed 's/ /%20/g'|sed 's/\\+/%2B/g'`
		file_ext=`echo "${file}"|awk -F . '{print $NF}'`
		if test "${file}" == "${file_ext}"; then
			file_base="${file}"
		else
			file_base=`basename "${file}" ".${file_ext}"`
		fi

		echo "<item>"
		echo "<title>${file}</title>"
		echo "<description>${file}</description>"
		torrent_file="${torrent_directory}/${file}.torrent"

		info=`/bin/ls -o "${target}" 2>/dev/null |cut -d" " -f4-|sed 's/^ *//'`
		total=`echo "${total}+1"|bc`
		size=`echo ${info}|cut -d' ' -f1-1|tr -d " "`
		user=`/bin/ls -o ${target}|awk '{print $3}'`
		content_type=`file -Lib "${upload_directory}/${file}"`

		echo "<guid>${upload_url}/${file_c}</guid>"
		echo "<link>${upload_url}/${file_c}</link>"
		echo "<enclosure url=\"${upload_url}/${file_c}\" length=\"${size}\" type=\"${content_type}\"/>"

		echo "</item>"

		if test "${total}" = "${max_show}"; then
			break;
		fi
	fi
done
}

echo "</channel></rss>"

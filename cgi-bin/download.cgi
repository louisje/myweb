#!/bin/bash

eval "`./proccgi $*`"

max_show="15"
http_user="apache"
mktorrent="/usr/bin/mktorrent"
tracker="http://thepiratebay.org/announce"
torrent_directory="/home/louis/public_html/torrents"
torrent_url="http://teltel.co.cc/louis/torrents"
upload_directory="/home/louis/public_html/downloads"
upload_url="http://teltel.co.cc/louis/downloads"
tmp_directory="/var/tmp"
log_directory="/home/louis/public_html/myweb/logs"

echo "Content-Type: text/html"
echo ""
echo "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">"
echo "<html>"
echo "<head>"
echo "<meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\">"
echo "<title>檔案櫃</title>"
echo "</head>"
echo "<body background=\"../images/bg.gif\">"

if test ! -f "${mktorrent}"; then
	error="mktorrent doesn't exists!"
fi

if test ! -d "${torrent_directory}" -o ! -w "${torrent_directory}"; then
	error="torrent_directory isn't writable!"
fi

if test ! -d "${upload_directory}" -o ! -w "${upload_directory}"; then
	error="upload_directory isn't writable!"
fi

pass_hash=`echo "${FORM_pass}" | md5sum | cut -c1-32`
torrentize=`echo -e "${FORM_torrentize}"`
detorrentize=`echo -e "${FORM_detorrentize}"`
mode=`echo -e "${FORM_mode}"`
mailto=`echo -e "${FORM_mailto}"`

if test "${pass_hash}" = "5df03f95b4ff4f4b5dabe53a5a1e15d7"; then
	mode="admin"
fi

robot=`echo "${HTTP_USER_AGENT}" | grep "Googlebot"`
if test "${mode}" != "EmailPush"; then
	echo "<form method=\"post\" action=\"remove.cgi\" style=\"margin:0px\">"
	echo "<b>已上傳的檔案：</b><small>"
else
	echo "<form method=\"post\" action=\"download.cgi?mode=EmailPush\" style=\"margin:0px\">"
	echo "<b>已製作的torrent：</b><small>"
fi
if test ! -n "${robot}"; then
	echo "<font color=\"gray\">[ </font>"
	echo "<a href=\"./download.cgi\">下載模式</a> <font color=\"gray\">|</font> <a href=\"./download.cgi?pass=upload\">管理模式</a> <font color=\"gray\">|</font> <a href=\"./download.cgi?mode=EmailPush\">EmailPush模式</a>"
	echo "<font color=\"gray\">|</font> <a href=\"rss.cgi\"><img src=\"http://calendar.uoregon.edu/images/rss_new.gif\" alt=\"RSS validator\"></a>"
	echo "<font color=\"gray\"> ]</font>"
fi
echo "<!-- Log Info"
log_info="["`date '+%T'`"] ${REMOTE_ADDR}:${REMOTE_PORT}"
log_file="${log_directory}/"`date '+%F'`".log"
echo "${log_info} |      user_agent | ${HTTP_USER_AGENT}" | tee -a "${log_file}"
echo "-->"
if test -n "${error}"; then
	echo "<font color=\"red\">${error}</font>";
elif test -n "${robot}"; then
	echo "<!-- Hello Robot -->"
elif test -n "${torrentize}"; then
	echo "<!--"
	cd "${torrent_directory}"
	if test -f "${torrentize}.torrent"; then
		rm -f -v "${torrentize}.torrent"
	fi
	${mktorrent} -v -a "${tracker}" "${upload_directory}/${torrentize}" 2>&1
	echo "${log_info} |       mktorrent | ${torrentize}" | tee -a "${log_file}"
	echo "-->"
	echo "<font color=\"darkgreen\">己送出製作 torrent 的請求</font>"
elif test -n "${detorrentize}"; then
	echo "<!--"
	cd "${torrent_directory}"
	if test -f "${detorrentize}.torrent"; then
		rm -f -v "${detorrentize}.torrent"
	fi
	echo "${log_info} |  remove_torrent | ${detorrentize}" | tee -a "${log_file}"
	echo "-->"
	echo "<font color=\"darkred\">torrent 檔己刪除</font>"
elif test -n "${mailto}"; then
	echo "<!--"
	echo "mailto: ${mailto}"
	echo "url: http://${SERVER_ADDR}${REQUEST_URI}"
	curl "http://${SERVER_ADDR}${REQUEST_URI}" | mail -v -s "~ Everybody Hates Chris ~" "${mailto}"
	echo "-->"
	echo "<font color=\"darkgreen\">信件己送出</font>"
else
	echo "<!-- Enviroment Variables"
	env
	echo "-->"
fi
echo "</small><br>"

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

		torrent_file="${torrent_directory}/${file}.torrent"
		temp="<input type=\"checkbox\" name=\"delete\" value=\"${file}\""
		if test "${mode}" == "EmailPush"; then
			echo ""
		elif test "`/bin/ls -o "${upload_directory}/${file}"|awk '{print $3}'`" != "${http_user}"; then
			echo "<span style=\"color:orange\">＊</span>"
		else
			if test "${mode}" == "admin" -a ! -f "${torrent_file}"; then
				echo "${temp}>"
			else
				echo "${temp} disabled=\"disabled\">"
			fi
		fi

		if test "${mode}" == "admin"; then
			echo "${file}<small style=\"color:gray\">" 
		elif test "${mode}" == "EmailPush"; then
			echo ""
		else
			echo "<a href=\"${upload_url}/${file_c}\">${file}</a><small style=\"color:gray\">" 
		fi

		info=`/bin/ls -o "${target}" 2>/dev/null |cut -d" " -f4-|sed 's/^ *//'`
		total=`echo "${total}+1"|bc`
		if test "${mode}" == "EmailPush"; then
			echo ""
		elif test -f "${target}"; then
			size=`echo ${info}|cut -d' ' -f1-1|tr -d " "`
			usage=`echo "${usage}+${size}"|bc`
			if test "${size}" -le "1048576"; then
				size=`echo "${size}/1024+1"|bc`
				echo "( ${size} KB )"
			else
				m_size=`echo "${size}/1048576"|bc`
				size=`echo "(${size}%1048576)/10485.76"|bc`
				size=`printf "%02d" $size`
				echo "( ${m_size}.${size} MB )"
			fi
			echo "<i>"`echo ${info}|cut -d' ' -f2-4`"</i>"
			user=`/bin/ls -o ${target}|awk '{print $3}'`
			if test "${user}" != "${http_user}"; then
				if test "${mode}" == "admin"; then
					echo " - <span style=\"color:green\"><i>$user</i></span>"
				else
					echo " - <span style=\"color:green\"><i>站內連結</i></span>"
				fi
			fi
			file_exists="yes"
		else
			echo "( <font color="darkred">不存在</font> )"
			file_exists="no"
		fi

		if test -f "${torrent_file}"; then
			if test "${mode}" == "EmailPush"; then
				echo "<small>${torrent_url}/${file_c}.torrent"
			elif test "${mode}" != "admin"; then
				url="${torrent_url}/${file_c}.torrent"
				echo " - <a href=\"${url}\"><small><i>下載 torrent</i></small></a> ";
			fi
		fi

		if test "${mode}" == "admin"; then
			if test -f "${torrent_file}"; then
				echo " - <small>[ <a href=\"./download.cgi?pass=upload&amp;detorrentize=${file_c}\"><i>刪除 torrent</i></a> ]</small>"
			elif test "${file_exists}" == "yes"; then
				echo " - <small>[ <a href=\"./download.cgi?pass=upload&amp;torrentize=${file_c}\"><i>Torrentize It</i></a> ]</small>"
			fi
		fi

		if test "${mode}" != "EmailPush" -o -f "${torrent_file}"; then
			echo "</small><br>"
		fi
		if test "${FORM_showall}" != "1" -a "${total}" = "${max_show}"; then
			break;
		fi
	fi
done
if test "${mode}" != "EmailPush"; then
	usage=`echo "${usage}/1048576"|bc`
	if test "${mode}" == "admin"; then
		echo "<input type=\"submit\" value=\"刪除\"> "
	else
		echo "<input type=\"submit\" value=\"刪除\" disabled=\"disabled\"> "
	fi
	free=`/bin/df ${tmp_directory}|tail -1|awk '{print $4}'`
	free=`echo "${free}/1024"|bc`
	echo "<small>( 顯示 ${total} 個檔案，使用 ${usage} MB，剩餘 ${free} MB) "
	if test "${FORM_showall}" != "1" -a "${total}" = "${max_show}"; then
		echo "『<a href=\"download.cgi?showall=1&amp;${QUERY_STRING}\">顯示全部檔案</a>』"
	fi
	echo "</small>"
else
	echo "<label>MailPush：</label>"
	echo "<input type=\"text\" name=\"mailto\" size=\"20\">"
	echo "<input type=\"hidden\" name=\"mode\" value=\"EmailPush\">"
	echo "<input type=\"submit\" value=\"發送信件\">"
fi
echo "</form>"
}

echo "<p align=\"right\">"
echo "<a href=\"http://validator.w3.org/check?uri=referer\"><img"
echo "   src=\"http://www.w3.org/Icons/valid-html401\""
echo "   alt=\"Valid HTML 4.01 Transitional\" border=\"0\" height=\"31\" width=\"88\"></a>"
echo "</p>"
echo "</body></html>"

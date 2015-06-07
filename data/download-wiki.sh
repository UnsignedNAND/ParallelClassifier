#!/usr/bin/env bash

# Script aids in getting appropriate Wikipedia database dump, as they are obviously too big to be inclused in repository.
# NOTE: files can be multiple gigabytes in size.

online_dumps=(
    "https://dumps.wikimedia.org/simplewiki/20150314/simplewiki-20150314-pages-articles.xml.bz2"
    "https://dumps.wikimedia.org/enwiki/20150304/enwiki-20150304-pages-articles.xml.bz2"
)

printf "Available Wikipedia database dumps to download [%s]:\n" ${#online_dumps[*]}
for index in ${!online_dumps[*]}
do
    printf "%4d: %s\n" $index ${online_dumps[$index]}
done
read -p "Index you want to download (supports resume):" index

echo Downloading...
if [ $index -ge 0 ] && [ $index -lt ${#online_dumps[*]} ]; then
    wget -c ${online_dumps[$index]}
fi

archive_name=`basename ${online_dumps[$index]}`
echo Unpacking...
bzip2 -dk $archive_name

echo Creating symlink: wiki_dump.xml
rm wiki_dump.xml 2> /dev/null
dump_name=${archive_name//.bz2}
ln -s $dump_name wiki_dump.xml

#!/bin/bash

set -euo pipefail

# Force default language for output sorting to be bytewise. Necessary to ensure uniformity amongst
# UNIX commands.
export LC_ALL=C
ROOT_DIR=`pwd`
OUT_DIR="dump"

DOWNLOAD_URL="https://dumps.wikimedia.org/enwiki/$DOWNLOAD_DATE"
TORRENT_URL="https://dump-torrents.toolforge.org/enwiki/$DOWNLOAD_DATE"

SHA1SUM_FILENAME="enwiki-$DOWNLOAD_DATE-sha1sums.txt"
REDIRECTS_FILENAME="enwiki-$DOWNLOAD_DATE-redirect.sql.gz"
PAGES_FILENAME="enwiki-$DOWNLOAD_DATE-page.sql.gz"
LINKS_FILENAME="enwiki-$DOWNLOAD_DATE-pagelinks.sql.gz"


###########################################
#  REPLACE TITLES AND REDIRECTS IN FILES  #
###########################################
if [ ! -f redirects.with_ids.txt.gz ]; then
  echo
  echo "[INFO] Replacing titles in redirects file"
  time python "$ROOT_DIR/replace_titles_in_redirects_file.py" pages.txt.gz redirects.txt.gz \
    | sort -S 100% -t $'\t' -k 1n,1n \
    | pigz --fast > redirects.with_ids.txt.gz.tmp
  mv redirects.with_ids.txt.gz.tmp redirects.with_ids.txt.gz
else
  echo "[WARN] Already replaced titles in redirects file"
fi

echo "[DEBUG] done with replacing titles and redirects"

if [ ! -f links.with_ids.txt.gz ]; then
  echo
  echo "[INFO] Replacing titles and redirects in links file"
  time python "$ROOT_DIR/replace_titles_and_redirects_in_links_file.py" pages.txt.gz redirects.with_ids.txt.gz links.txt.gz \
    | pigz --fast > links.with_ids.txt.gz.tmp
  mv links.with_ids.txt.gz.tmp links.with_ids.txt.gz
else
  echo "[WARN] Already replaced titles and redirects in links file"
fi

if [ ! -f pages.pruned.txt.gz ]; then
  echo
  echo "[INFO] Pruning pages which are marked as redirects but with no redirect"
  time python "$ROOT_DIR/prune_pages_file.py" pages.txt.gz redirects.with_ids.txt.gz \
    | pigz --fast > pages.pruned.txt.gz
else
  echo "[WARN] Already pruned pages which are marked as redirects but with no redirect"
fi

echo "[DEBUG] done with titles and redirects in links file"

#####################
#  SORT LINKS FILE  #
#####################
if [ ! -f links.sorted_by_source_id.txt.gz ]; then
  echo
  echo "[INFO] Sorting links file by source page ID"
  time pigz -dc links.with_ids.txt.gz \
    | sort -S 80% -t $'\t' -k 1n,1n \
    | uniq \
    | pigz --fast > links.sorted_by_source_id.txt.gz.tmp
  mv links.sorted_by_source_id.txt.gz.tmp links.sorted_by_source_id.txt.gz
else
  echo "[WARN] Already sorted links file by source page ID"
fi

echo "[DEBUG] done with sorting links file"

if [ ! -f links.sorted_by_target_id.txt.gz ]; then
  echo
  echo "[INFO] Sorting links file by target page ID"
  time pigz -dc links.with_ids.txt.gz \
    | sort -S 80% -t $'\t' -k 2n,2n \
    | uniq \
    | pigz --fast > links.sorted_by_target_id.txt.gz.tmp
  mv links.sorted_by_target_id.txt.gz.tmp links.sorted_by_target_id.txt.gz
else
  echo "[WARN] Already sorted links file by target page ID"
fi

echo "[DEBUG] done with sorting by target ID"

#############################
#  GROUP SORTED LINKS FILE  #
#############################
if [ ! -f links.grouped_by_source_id.txt.gz ]; then
  echo
  echo "[INFO] Grouping source links file by source page ID"
  time pigz -dc links.sorted_by_source_id.txt.gz \
   | awk -F '\t' '$1==last {printf "|%s",$2; next} NR>1 {print "";} {last=$1; printf "%s\t%s",$1,$2;} END{print "";}' \
   | pigz --fast > links.grouped_by_source_id.txt.gz.tmp
  mv links.grouped_by_source_id.txt.gz.tmp links.grouped_by_source_id.txt.gz
else
  echo "[WARN] Already grouped source links file by source page ID"
fi

echo "[DEBUG] done with grouping source links file"

if [ ! -f links.grouped_by_target_id.txt.gz ]; then
  echo
  echo "[INFO] Grouping target links file by target page ID"
  time pigz -dc links.sorted_by_target_id.txt.gz \
    | awk -F '\t' '$2==last {printf "|%s",$1; next} NR>1 {print "";} {last=$2; printf "%s\t%s",$2,$1;} END{print "";}' \
    | gzip > links.grouped_by_target_id.txt.gz
else
  echo "[WARN] Already grouped target links file by target page ID"
fi

echo "[DEBUG] done with grouping by target page ID"

################################
# COMBINE GROUPED LINKS FILES  #
################################
if [ ! -f links.with_counts.txt.gz ]; then
  echo
  echo "[INFO] Combining grouped links files"
  time python "$ROOT_DIR/combine_grouped_links_files.py" links.grouped_by_source_id.txt.gz links.grouped_by_target_id.txt.gz \
    | pigz --fast > links.with_counts.txt.gz.tmp
  mv links.with_counts.txt.gz.tmp links.with_counts.txt.gz
else
  echo "[WARN] Already combined grouped links files"
fi

echo "[DEBUG] done with grouping"

############################
#  CREATE SQLITE DATABASE  #
############################
if [ ! -f sdow.sqlite ]; then
  echo
  echo "[INFO] Creating redirects table"
  time pigz -dc redirects.with_ids.txt.gz | sqlite3 sdow.sqlite ".read $ROOT_DIR/../sql/createRedirectsTable.sql"

  echo
  echo "[INFO] Creating pages table"
  time pigz -dc pages.pruned.txt.gz | sqlite3 sdow.sqlite ".read $ROOT_DIR/../sql/createPagesTable.sql"

  echo
  echo "[INFO] Creating links table"
  time pigz -dc links.with_counts.txt.gz | sqlite3 sdow.sqlite ".read $ROOT_DIR/../sql/createLinksTable.sql"

  echo
  echo "[INFO] Compressing SQLite file"
  time pigz --best --keep sdow.sqlite
else
  echo "[WARN] Already created SQLite database"
fi


echo
echo "[INFO] All done!"

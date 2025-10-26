#!/bin/bash

set -euo pipefail

# Force default language for output sorting to be bytewise. Necessary to ensure uniformity amongst
# UNIX commands.
export LC_ALL=C

# By default, the latest Wikipedia dump will be downloaded. If a download date in the format
# YYYYMMDD is provided as the first argument, it will be used instead.
if [[ $# -eq 0 ]]; then
  DOWNLOAD_DATE=$(wget -q -O- https://dumps.wikimedia.org/plwiki/ | grep -Po '\d{8}' | sort | tail -n1)
else
  if [ ${#1} -ne 8 ]; then
    echo "[ERROR] Invalid download date provided: $1"
    exit 1
  else
    DOWNLOAD_DATE=$1
  fi
fi

ROOT_DIR=`pwd`
OUT_DIR="dump"

DOWNLOAD_URL="https://dumps.wikimedia.org/plwiki/$DOWNLOAD_DATE"
TORRENT_URL="https://dump-torrents.toolforge.org/plwiki/$DOWNLOAD_DATE"

SHA1SUM_FILENAME="plwiki-$DOWNLOAD_DATE-sha1sums.txt"
REDIRECTS_FILENAME="plwiki-$DOWNLOAD_DATE-redirect.sql.gz"
PAGES_FILENAME="plwiki-$DOWNLOAD_DATE-page.sql.gz"
LINKS_FILENAME="plwiki-$DOWNLOAD_DATE-pagelinks.sql.gz"


# Make the output directory if it doesn't already exist and move to it
mkdir -p $OUT_DIR
pushd $OUT_DIR > /dev/null


echo "[INFO] Download date: $DOWNLOAD_DATE"
echo "[INFO] Download URL: $DOWNLOAD_URL"
echo "[INFO] Output directory: $OUT_DIR"
echo

##############################
#  DOWNLOAD WIKIPEDIA DUMPS  #
##############################

function download_file() {
  if [ ! -f $2 ]; then
    echo
    if [ $1 != sha1sums ] && command -v aria2c > /dev/null; then
      echo "[INFO] Downloading $1 file via torrent"
      time aria2c --summary-interval=0 --console-log-level=warn --seed-time=0 \
        "$TORRENT_URL/$2.torrent" 2>&1 | grep -v "ERROR\|Exception" || true
    fi
    
    if [ ! -f $2 ]; then
      echo "[INFO] Downloading $1 file via wget"
      time wget --progress=dot:giga "$DOWNLOAD_URL/$2"
    fi

    if [ $1 != sha1sums ]; then
      echo
      echo "[INFO] Verifying SHA-1 hash for $1 file"
      time grep "$2" "$SHA1SUM_FILENAME" | sha1sum -c
      if [ $? -ne 0 ]; then
        echo
        echo "[ERROR] Downloaded $1 file has incorrect SHA-1 hash"
        rm $2
        exit 1
      fi
    fi
  else
    echo "[WARN] Already downloaded $1 file"
  fi
}

download_file "sha1sums" $SHA1SUM_FILENAME
download_file "redirects" $REDIRECTS_FILENAME
download_file "pages" $PAGES_FILENAME
download_file "links" $LINKS_FILENAME

##########################
#  TRIM WIKIPEDIA DUMPS  #
##########################

#we dont have this file yet
if [ ! -f redirects.txt.gz ]; then 
  echo
  echo "[INFO] Trimming redirects file"

  # Unzip
  # Remove all lines that don't start with INSERT INTO...
  # Split into individual records
  # Only keep records in namespace 0
  # Replace namespace with a tab
  # Remove everything starting at the to page name's closing apostrophe
  # Zip into output file
  time pigz -dc $REDIRECTS_FILENAME \
    | sed -n 's/^INSERT INTO `redirect` VALUES (//p' \
    | sed -e 's/),(/\'$'\n/g' \
    | egrep "^[0-9]+,0," \
    | sed -e $"s/,0,'/\t/g" \
    | sed -e "s/','.*//g" \
    | pigz --fast > redirects.txt.gz.tmp
  mv redirects.txt.gz.tmp redirects.txt.gz
else
  echo "[WARN] Already trimmed redirects file"
fi

echo
echo "[DEBUG] Trimmed redirects file"

if [ ! -f pages.txt.gz ]; then
  echo
  echo "[INFO] Trimming pages file"

  # Unzip
  # Remove all lines that don't start with INSERT INTO...
  # Split into individual records
  # Only keep records in namespace 0
  # Replace namespace with a tab
  # Splice out the page title and whether or not the page is a redirect
  # Zip into output file
  time pigz -dc $PAGES_FILENAME \
    | sed -n 's/^INSERT INTO `page` VALUES (//p' \
    | sed -e 's/),(/\'$'\n/g' \
    | egrep "^[0-9]+,0," \
    | sed -e $"s/,0,'/\t/" \
    | sed -e $"s/',[^,]*,\([01]\).*/\t\1/" \
    | pigz --fast > pages.txt.gz.tmp
  mv pages.txt.gz.tmp pages.txt.gz
else
  echo "[WARN] Already trimmed pages file"
fi

echo
echo "[DEBUG] Trimmed pages file"

if [ ! -f links.txt.gz ]; then
  echo
  echo "[INFO] Trimming links file"

  # Unzip
  # Remove all lines that don't start with INSERT INTO...
  # Split into individual records
  # Only keep records in namespace 0
  # Replace namespace with a tab
  # Remove everything starting at the to page name's closing apostrophe
  # Zip into output file
  time pigz -dc $LINKS_FILENAME \
    | sed -n 's/^INSERT INTO `pagelinks` VALUES (//p' \
    | sed -e 's/),(/\'$'\n/g' \
    | egrep "^[0-9]+,0,[0-9]+$" \
    | sed -e 's/,0,/\t/g' \
    | pigz --fast > links.txt.gz.tmp
  mv links.txt.gz.tmp links.txt.gz
else
  echo "[WARN] Already trimmed links file"
fi

echo 
echo "[DEBUG] Trimmed links file"

echo "All done with preprocessing"

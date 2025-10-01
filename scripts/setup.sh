set -euo pipefail

DATE="20250920"      # change to latest dump date
WIKI="plwiki"
DUMP_URL="https://dumps.wikimedia.org/$WIKI/$DATE"
DB_NAME="wikipedia"
MYSQL="sudo mysql -u root $DB_NAME"

mkdir -p dumps
cd dumps

wget -c https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-redirect.sql.gz
wget -c https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-pagelinks.sql.gz
wget -c https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-page.sql.gz

cd .. 

sudo mysql -u root -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME;"

zcat dumps/plwiki-latest-page.sql.gz       | $MYSQL
zcat dumps/plwiki-latest-pagelinks.sql.gz | $MYSQL
zcat dumps/plwiki-latest-redirect.sql.gz  | $MYSQL

$MYSQL < preprocess.sql

echo "all done!"

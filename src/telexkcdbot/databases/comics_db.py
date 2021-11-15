from asyncpg import Pool, Record
from src.telexkcdbot.models import ComicData, ComicHeadlineInfo
from typing import List


class ComicsDatabase:
    pool: Pool

    async def create(self, pool: Pool):
        self.pool = pool
        query = """CREATE TABLE IF NOT EXISTS comics (
                     id SERIAL NOT NULL,
                     comic_id INTEGER NOT NULL UNIQUE,
                     title VARCHAR(128) DEFAULT '...',
                     img_url VARCHAR(512) DEFAULT '',
                     comment TEXT DEFAULT '...',
                     public_date DATE NOT NULL DEFAULT CURRENT_DATE,
                     is_specific BOOLEAN DEFAULT FALSE,
                     ru_title VARCHAR(128) DEFAULT '...',
                     ru_img_url VARCHAR(512) DEFAULT '...',
                     ru_comment TEXT DEFAULT '...',
                     has_ru_translation BOOLEAN DEFAULT FALSE);

                   CREATE UNIQUE INDEX IF NOT EXISTS comic_id_uindex ON comics (comic_id);"""

        await self.pool.execute(query)

    @staticmethod
    async def records_to_headlines_info(records: List[Record], title_col: str, img_url_col: str):
        headlines_info = []
        for record in records:
            headline_info = ComicHeadlineInfo(comic_id=record['comic_id'],
                                              title=record[title_col],
                                              img_url=record[img_url_col])
            headlines_info.append(headline_info)
        return headlines_info

    async def add_new_comic(self, comic_values: tuple):
        query = """INSERT INTO comics (comic_id,
                                       title,
                                       img_url,
                                       comment,
                                       public_date,
                                       is_specific,
                                       ru_title,
                                       ru_img_url,
                                       ru_comment,
                                       has_ru_translation)
                   VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                   ON CONFLICT (comic_id) DO NOTHING;"""

        await self.pool.execute(query, *comic_values)

    async def get_all_comics_ids(self) -> tuple:
        query = """SELECT array_agg(comic_id) FROM comics;"""

        res = await self.pool.fetchval(query)

        return tuple(res) if res else ()

    async def get_last_comic_id(self) -> int:
        query = """SELECT comic_id FROM comics
                   ORDER BY comic_id DESC;"""

        res = await self.pool.fetchval(query)

        return res

    async def get_comic_data_by_id(self, comic_id: int, comic_lang='en') -> ComicData:
        if comic_lang == 'en':
            query = """SELECT comic_id, title, img_url, comment, public_date, is_specific, has_ru_translation 
                       FROM comics
                       WHERE comic_id = $1;"""
        else:
            query = """SELECT comic_id, ru_title, ru_img_url, ru_comment, public_date, is_specific, has_ru_translation 
                       FROM comics
                       WHERE comic_id = $1;"""

        res = await self.pool.fetchrow(query, comic_id)

        comic_data = ComicData(*res)
        return comic_data

    async def get_comics_headlines_info_by_title(self, title: str, lang: str = 'en') -> List[ComicHeadlineInfo]:
        assert lang in ('ru', 'en')

        # TODO: не находит RTL
        # TODO: по superm не находит Bird/Plane/Superman
        title_col, img_url_col = ('title', 'img_url') if lang == 'en' else ('ru_title', 'ru_img_url')
        query = f"""SELECT comic_id, {title_col}, {img_url_col} FROM comics

                     WHERE {title_col} = $1
                     OR {title_col} ILIKE format('%s %s%s', '%', $1, '%')
                     OR {title_col} ILIKE format('%s%s', $1, '%')
                     OR {title_col} ILIKE format('%s%s %s', '%', $1, '%')
                     OR {title_col} ILIKE format('%s%s', '%', $1)
                     OR {title_col} ILIKE format('%s%s, %s', '%', $1, '%')
                     OR {title_col} ILIKE format('%s%s-%s', '%', $1, '%')
                     OR {title_col} ILIKE format('%s-%s%s', '%', $1, '%')"""

        res = await self.pool.fetch(query, title)
        if not res:
            return []
        return await self.records_to_headlines_info(sorted(res, key=lambda x: len(x[title_col])),
                                                    title_col,
                                                    img_url_col)

    async def get_comics_headlines_info_by_ids(self, ids: list, lang: str = 'en') -> List[ComicHeadlineInfo]:
        assert lang in ('ru', 'en')

        title_col, img_url_col = ('title', 'img_url') if lang == 'en' else ('ru_title', 'ru_img_url')

        query = f"""SELECT comic_id, {title_col}, {img_url_col} FROM comics
                    WHERE comic_id in {tuple(ids)}"""

        res = await self.pool.fetch(query)
        headlines_info = await self.records_to_headlines_info(res, title_col, img_url_col)
        return [h for h in sorted(headlines_info, key=lambda x: ids.index(x.comic_id))]  # Saved order of bookmarks

    async def toggle_spec_status(self, comic_id: int):
        get_query = """SELECT is_specific FROM comics
                       WHERE comic_id = $1;"""

        set_query = """UPDATE comics SET is_specific = $1
                       WHERE comic_id = $2;"""

        async with self.pool.acquire() as conn:
            cur_value = await conn.fetchval(get_query, comic_id)
            await conn.execute(set_query, not cur_value, comic_id)


comics_db = ComicsDatabase()
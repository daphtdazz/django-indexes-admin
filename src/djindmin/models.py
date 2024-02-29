import logging
import re

from django.db import models


log = logging.getLogger(__name__)


class AModel(models.Model):
    name = models.CharField(max_length=1000)


class BModel(models.Model):
    name = models.CharField(max_length=1000)

    a_model = models.ForeignKey(AModel, on_delete=models.CASCADE)



class Index(models.Model):
    schemaname = models.CharField()
    tablename = models.CharField()
    indexname = models.CharField(primary_key=True)
    indexdef = models.TextField()

    class Meta:
        managed = False
        db_table = "django_indexes_view"
        verbose_name_plural = "indexes"

    def save(self):
        log.info("Save index")

    @property
    def _parsed_create_sql(self):
        """
        From https://www.postgresql.org/docs/16/sql-createindex.html
        CREATE [ UNIQUE ] INDEX [ CONCURRENTLY ] [ [ IF NOT EXISTS ] name ] ON [ ONLY ] table_name
            [ USING method ]
        ( { column_name | ( expression ) }
        [ COLLATE collation ]
        [ opclass [ ( opclass_parameter = value [, ... ] ) ] ]
        [ ASC | DESC ] [ NULLS { FIRST | LAST } ] [, ...] )
        [ INCLUDE ( column_name [, ...] ) ]
        [ NULLS [ NOT ] DISTINCT ]
        [ WITH ( storage_parameter [= value] [, ... ] ) ]
        [ TABLESPACE tablespace_name ]
        [ WHERE predicate ]
        """
        mo = re.match(
            r"\s*CREATE\s+(UNIQUE\s+)?"  # 1
            r"INDEX\s+(\w+)\s+"  # 2
            r"ON\s+(ONLY\s+)?"  # 3
            r"([\w.]+)"  # 4
            r"\s+USING\s+(\w+)", # 5
            self.indexdef,
            flags=re.IGNORECASE
        )

        if not mo:
            return None

        is_unique = bool(mo.group(1))
        name = mo.group(2)
        only = bool(mo.group(3))
        table = mo.group(4)
        method = mo.group(5)

        return (is_unique, name, only, table, method)

    @property
    def is_unique(self) -> bool:
        return self._parsed_create_sql and self._parsed_create_sql[0]

    @property
    def method(self):
        return self._parsed_create_sql and self._parsed_create_sql[4]

    def __str__(self):
        return f"{self.schemaname}.{self.tablename}"


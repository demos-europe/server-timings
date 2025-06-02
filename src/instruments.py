import logging
import sqlparse
from .models import ServerTimingMetric


class DBQueryInstrument:
    def __init__(self, timings):
        self.counter = 0
        self.timings = timings

    def __call__(self, execute, sql: str, params, many, context):
        metric = ServerTimingMetric(name=f"db_{self.counter+1}", description="", timings=self.timings)

        try:
            metric.start()
            self.counter += 1
            result = execute(sql, params, many, context)
        except Exception as e:
            raise e
        else:
            return result
        finally:
            metric.description = self.execution_info(sql)
            metric.end()

    def execution_info(self, sql) -> str:
        if len(sql) < 20:
            return sql
        parsed = sqlparse.parse(sql)[0]
        tokens = [token for token in parsed.tokens if not token.is_whitespace]

        operation = tokens[0].value.upper()  # First token is typically the operation (SELECT, INSERT, etc.)
        table_name = None

        match operation:
            case "SET":
                table_name_token_prefix = "SET"
            case "INSERT":
                table_name_token_prefix = "INTO"
            case "UPDATE":
                table_name_token_prefix = "TABLE"
            case "DELETE", "SELECT":
                table_name_token_prefix = "FROM"
            case "SELECT":
                table_name_token_prefix = "FROM"
            case _:
                logging.warning(f"[DatabaseQueryTiming] Unsupported operation: {operation}")
                table_name_token_prefix = None

        if table_name_token_prefix:
            for i in range(len(tokens)):
                token = tokens[i]
                if token.ttype == sqlparse.tokens.Keyword and token.value.upper() == table_name_token_prefix:
                    table_name = str(tokens[i + 1].value).replace("\"", "'")
                    break

        return "DB: " + operation + " " + (table_name or "")


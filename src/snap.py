from typing import Any, Optional, List, TypeVar, Type, Callable, cast
from enum import Enum


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Function:
    function_name: str
    function_language: str
    function_def: str
    function_arguments: str
    return_type: str

    def __init__(self, function_name: str, function_language: str, function_def: str, function_arguments: str, return_type: str) -> None:
        self.function_name = function_name
        self.function_language = function_language
        self.function_def = function_def
        self.function_arguments = function_arguments
        self.return_type = return_type

    @staticmethod
    def from_dict(obj: Any) -> 'Function':
        assert isinstance(obj, dict)
        function_name = from_str(obj.get("function_name"))
        function_language = from_str(obj.get("function_language"))
        function_def = from_str(obj.get("function_def"))
        function_arguments = from_str(obj.get("function_arguments"))
        return_type = from_str(obj.get("return_type"))
        return Function(function_name, function_language, function_def, function_arguments, return_type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["function_name"] = from_str(self.function_name)
        result["function_language"] = from_str(self.function_language)
        result["function_def"] = from_str(self.function_def)
        result["function_arguments"] = from_str(self.function_arguments)
        result["return_type"] = from_str(self.return_type)
        return result


class IsNullable(Enum):
    NO = "NO"
    YES = "YES"


class Column:
    column_name: str
    data_type: str
    character_maximum_length: Optional[int]
    numeric_precision: Optional[int]
    numeric_scale: Optional[int]
    column_default: Optional[str]
    is_nullable: IsNullable
    ordinal_position: int

    def __init__(self, column_name: str, data_type: str, character_maximum_length: Optional[int], numeric_precision: Optional[int], numeric_scale: Optional[int], column_default: Optional[str], is_nullable: IsNullable, ordinal_position: int) -> None:
        self.column_name = column_name
        self.data_type = data_type
        self.character_maximum_length = character_maximum_length
        self.numeric_precision = numeric_precision
        self.numeric_scale = numeric_scale
        self.column_default = column_default
        self.is_nullable = is_nullable
        self.ordinal_position = ordinal_position

    @staticmethod
    def from_dict(obj: Any) -> 'Column':
        assert isinstance(obj, dict)
        column_name = from_str(obj.get("column_name"))
        data_type = from_str(obj.get("data_type"))
        character_maximum_length = from_union([from_none, from_int], obj.get("character_maximum_length"))
        numeric_precision = from_union([from_none, from_int], obj.get("numeric_precision"))
        numeric_scale = from_union([from_none, from_int], obj.get("numeric_scale"))
        column_default = from_union([from_none, from_str], obj.get("column_default"))
        is_nullable = IsNullable(obj.get("is_nullable"))
        ordinal_position = from_int(obj.get("ordinal_position"))
        return Column(column_name, data_type, character_maximum_length, numeric_precision, numeric_scale, column_default, is_nullable, ordinal_position)

    def to_dict(self) -> dict:
        result: dict = {}
        result["column_name"] = from_str(self.column_name)
        result["data_type"] = from_str(self.data_type)
        result["character_maximum_length"] = from_union([from_none, from_int], self.character_maximum_length)
        result["numeric_precision"] = from_union([from_none, from_int], self.numeric_precision)
        result["numeric_scale"] = from_union([from_none, from_int], self.numeric_scale)
        result["column_default"] = from_union([from_none, from_str], self.column_default)
        result["is_nullable"] = to_enum(IsNullable, self.is_nullable)
        result["ordinal_position"] = from_int(self.ordinal_position)
        return result


class Constraint:
    constraint_type: str
    constraint_def: str

    def __init__(self, constraint_type: str, constraint_def: str) -> None:
        self.constraint_type = constraint_type
        self.constraint_def = constraint_def

    @staticmethod
    def from_dict(obj: Any) -> 'Constraint':
        assert isinstance(obj, dict)
        constraint_type = from_str(obj.get("constraint_type"))
        constraint_def = from_str(obj.get("constraint_def"))
        return Constraint(constraint_type, constraint_def)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constraint_type"] = from_str(self.constraint_type)
        result["constraint_def"] = from_str(self.constraint_def)
        return result


class Index:
    indexname: str
    indexdef: str

    def __init__(self, indexname: str, indexdef: str) -> None:
        self.indexname = indexname
        self.indexdef = indexdef

    @staticmethod
    def from_dict(obj: Any) -> 'Index':
        assert isinstance(obj, dict)
        indexname = from_str(obj.get("indexname"))
        indexdef = from_str(obj.get("indexdef"))
        return Index(indexname, indexdef)

    def to_dict(self) -> dict:
        result: dict = {}
        result["indexname"] = from_str(self.indexname)
        result["indexdef"] = from_str(self.indexdef)
        return result


class Table:
    table_name: str
    columns: List[Column]
    constraints: List[Constraint]
    indexes: List[Index]

    def __init__(self, table_name: str, columns: List[Column], constraints: List[Constraint], indexes: List[Index]) -> None:
        self.table_name = table_name
        self.columns = columns
        self.constraints = constraints
        self.indexes = indexes

    @staticmethod
    def from_dict(obj: Any) -> 'Table':
        assert isinstance(obj, dict)
        table_name = from_str(obj.get("table_name"))
        columns = from_list(Column.from_dict, obj.get("columns"))
        constraints = from_list(Constraint.from_dict, obj.get("constraints"))
        indexes = from_list(Index.from_dict, obj.get("indexes"))
        return Table(table_name, columns, constraints, indexes)

    def to_dict(self) -> dict:
        result: dict = {}
        result["table_name"] = from_str(self.table_name)
        result["columns"] = from_list(lambda x: to_class(Column, x), self.columns)
        result["constraints"] = from_list(lambda x: to_class(Constraint, x), self.constraints)
        result["indexes"] = from_list(lambda x: to_class(Index, x), self.indexes)
        return result


class Snap:
    schema: str
    tables: List[Table]
    functions: List[Function]

    def __init__(self, schema: str, tables: List[Table], functions: List[Function]) -> None:
        self.schema = schema
        self.tables = tables
        self.functions = functions

    @staticmethod
    def from_dict(obj: Any) -> 'Snap':
        assert isinstance(obj, dict)
        schema = from_str(obj.get("schema"))
        tables = from_list(Table.from_dict, obj.get("tables"))
        functions = from_list(Function.from_dict, obj.get("functions"))
        return Snap(schema, tables, functions)

    def to_dict(self) -> dict:
        result: dict = {}
        result["schema"] = from_str(self.schema)
        result["tables"] = from_list(lambda x: to_class(Table, x), self.tables)
        result["functions"] = from_list(lambda x: to_class(Function, x), self.functions)
        return result


def snap_from_dict(s: Any) -> Snap:
    return Snap.from_dict(s)


def snap_to_dict(x: Snap) -> Any:
    return to_class(Snap, x)

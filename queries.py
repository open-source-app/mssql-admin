
tables = """
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
      AND TABLE_NAME NOT LIKE 'sys%'
      AND TABLE_NAME NOT LIKE 'MS%';
      """

table_info = """
    SELECT 
        c.TABLE_NAME,
        c.COLUMN_NAME,
        c.DATA_TYPE,
        c.CHARACTER_MAXIMUM_LENGTH,
        c.NUMERIC_PRECISION,
        c.NUMERIC_SCALE,
        c.IS_NULLABLE,
        c.COLUMN_DEFAULT,
        CASE 
            WHEN ic.column_id IS NOT NULL THEN 'YES' ELSE 'NO'
        END AS HAS_IDENTITY,
        CAST(ic.SEED_VALUE AS NVARCHAR(255)) AS IDENTITY_SEED,
        CAST(ic.INCREMENT_VALUE AS NVARCHAR(255)) AS IDENTITY_INCREMENT,
        CASE 
            WHEN cc.column_id IS NOT NULL THEN 'YES' ELSE 'NO'
        END AS IsComputed,
        CAST(cc.definition AS NVARCHAR(MAX)) AS ComputedColumnDefinition,
        CASE 
            WHEN dc.definition IS NOT NULL THEN 'YES' ELSE 'NO'
        END AS HasDefaultConstraint,
        CAST(dc.definition AS NVARCHAR(MAX)) AS DefaultConstraintDefinition,
        fk.name AS ForeignKey,
        tp.name AS PrimaryTable,
        cp.name AS PrimaryColumn
    FROM 
        INFORMATION_SCHEMA.COLUMNS c
    LEFT JOIN 
        sys.tables t ON c.TABLE_NAME = t.name AND t.schema_id = SCHEMA_ID(c.TABLE_SCHEMA)
    LEFT JOIN 
        sys.columns sc ON t.object_id = sc.object_id AND c.COLUMN_NAME = sc.name
    LEFT JOIN 
        sys.identity_columns ic ON sc.object_id = ic.object_id AND sc.column_id = ic.column_id
    LEFT JOIN 
        sys.computed_columns cc ON sc.object_id = cc.object_id AND sc.column_id = cc.column_id
    LEFT JOIN 
        sys.default_constraints dc ON sc.default_object_id = dc.object_id
    LEFT JOIN 
        sys.foreign_key_columns AS fkc ON sc.object_id = fkc.parent_object_id AND sc.column_id = fkc.parent_column_id
    LEFT JOIN 
        sys.foreign_keys AS fk ON fkc.constraint_object_id = fk.object_id
    LEFT JOIN 
        sys.tables AS tp ON fkc.referenced_object_id = tp.object_id
    LEFT JOIN 
        sys.columns AS cp ON fkc.referenced_object_id = cp.object_id AND fkc.referenced_column_id = cp.column_id
    WHERE 
        c.TABLE_NAME = ?;
    """

foreign_keys = """SELECT 
    fk.name AS ForeignKey,
    tp.name AS PrimaryTable,
    cp.name AS PrimaryColumn,
    tf.name AS ForeignTable,
    cf.name AS ForeignColumn
FROM 
    sys.foreign_keys AS fk
INNER JOIN 
    sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN 
    sys.tables AS tp ON fkc.referenced_object_id = tp.object_id
INNER JOIN 
    sys.columns AS cp ON fkc.referenced_object_id = cp.object_id AND fkc.referenced_column_id = cp.column_id
INNER JOIN 
    sys.tables AS tf ON fkc.parent_object_id = tf.object_id
INNER JOIN 
    sys.columns AS cf ON fkc.parent_object_id = cf.object_id AND fkc.parent_column_id = cf.column_id
	WHERE tf.name = ?;"""

has_identity = """SELECT OBJECTPROPERTY(OBJECT_ID( ? ), 'TableHasIdentity') AS IDENTITY_INSERT_STATUS;"""

primary_key_column = """SELECT
    KU.TABLE_NAME,
    KU.COLUMN_NAME
FROM
    INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS TC
    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KU
        ON TC.CONSTRAINT_NAME = KU.CONSTRAINT_NAME
WHERE
    TC.CONSTRAINT_TYPE = 'PRIMARY KEY'
    AND KU.TABLE_NAME = ?;"""

table_offset_query ="""
SELECT *
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_NAME = ?
ORDER BY 
    COLUMN_NAME
OFFSET 
    ? ROWS FETCH NEXT ? ROWS ONLY;
""" 

type_of_key = """SELECT 
    fk.name AS ForeignKey,
    tp.name AS PrimaryTable,
    cp.name AS PrimaryColumn,
    tf.name AS ForeignTable,
    cf.name AS ForeignColumn,
    CASE
        WHEN pk.is_unique = 1 AND fk.is_unique = 1 THEN 'One-to-One'
        WHEN pk.is_unique = 1 AND fk.is_unique = 0 THEN 'One-to-Many'
        WHEN pk.is_unique = 0 AND fk.is_unique = 0 THEN 'Many-to-Many'
        ELSE 'Unknown'
    END AS RelationshipType
FROM 
    sys.foreign_keys AS fk
INNER JOIN 
    sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN 
    sys.tables AS tp ON fkc.referenced_object_id = tp.object_id
INNER JOIN 
    sys.columns AS cp ON fkc.referenced_object_id = cp.object_id AND fkc.referenced_column_id = cp.column_id
INNER JOIN 
    sys.tables AS tf ON fkc.parent_object_id = tf.object_id
INNER JOIN 
    sys.columns AS cf ON fkc.parent_object_id = cf.object_id AND fkc.parent_column_id = cf.column_id
INNER JOIN 
    sys.indexes AS pk ON tp.object_id = pk.object_id AND pk.is_primary_key = 1
INNER JOIN 
    sys.index_columns AS pkic ON pk.object_id = pkic.object_id AND pk.index_id = pkic.index_id AND pkic.column_id = cp.column_id
INNER JOIN 
    sys.indexes AS fkidx ON tf.object_id = fkidx.object_id AND fkidx.is_unique_constraint = 1
INNER JOIN 
    sys.index_columns AS fkic ON fkidx.object_id = fkic.object_id AND fkidx.index_id = fkic.index_id AND fkic.column_id = cf.column_id
WHERE 
    tf.name = ?;"""


{{ config(materialized='view') }}

-- Modèle staging : nettoyage léger, typage et renommage.
-- Basé sur l'EDA : pas de valeurs manquantes, pas de doublons,
-- pas de suppression d'outliers, pas de normalisation.
-- transaction_id est créé ici car il n'existe pas dans la table raw.transactions actuelle.

with source_transactions as (

    select *
    from raw.transactions

),

typed_transactions as (

    select
        row_number() over (order by time, amount, class) as transaction_id,
        cast(time as double) as transaction_time,

        cast(v1 as double) as v1,
        cast(v2 as double) as v2,
        cast(v3 as double) as v3,
        cast(v4 as double) as v4,
        cast(v5 as double) as v5,
        cast(v6 as double) as v6,
        cast(v7 as double) as v7,
        cast(v8 as double) as v8,
        cast(v9 as double) as v9,
        cast(v10 as double) as v10,
        cast(v11 as double) as v11,
        cast(v12 as double) as v12,
        cast(v13 as double) as v13,
        cast(v14 as double) as v14,
        cast(v15 as double) as v15,
        cast(v16 as double) as v16,
        cast(v17 as double) as v17,
        cast(v18 as double) as v18,
        cast(v19 as double) as v19,
        cast(v20 as double) as v20,
        cast(v21 as double) as v21,
        cast(v22 as double) as v22,
        cast(v23 as double) as v23,
        cast(v24 as double) as v24,
        cast(v25 as double) as v25,
        cast(v26 as double) as v26,
        cast(v27 as double) as v27,
        cast(v28 as double) as v28,

        cast(amount as double) as amount,
        cast(class as integer) as class

    from source_transactions

)

select *
from typed_transactions
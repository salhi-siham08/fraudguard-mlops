{{ config(materialized='table') }}

-- Mart ML : table finale prête pour la Personne 6.
-- Basé sur l'EDA :
-- 1. Création de features temporelles à partir de transaction_time.
-- 2. Création de amount_log car Amount est très asymétrique.
-- 3. Conservation de V1 à V28 pour laisser le choix au modèle ML.
-- 4. Aucune normalisation, aucun SMOTE, aucune suppression d'outliers dans dbt.

with transactions as (

    select *
    from {{ ref('stg_transactions') }}

),

features as (

    select
        transaction_id,
        transaction_time,

        floor(transaction_time / 3600) as transaction_hour_abs,
        mod(floor(transaction_time / 3600), 24) as transaction_hour,

        case
            when mod(floor(transaction_time / 3600), 24) between 0 and 5 then 1
            else 0
        end as is_night,

        amount,

        case
            when amount >= 0 then ln(amount + 1)
            else null
        end as amount_log,

        v1, v2, v3, v4, v5, v6, v7,
        v8, v9, v10, v11, v12, v13, v14,
        v15, v16, v17, v18, v19, v20, v21,
        v22, v23, v24, v25, v26, v27, v28,

        class

    from transactions

)

select *
from features
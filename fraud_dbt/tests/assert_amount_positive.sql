    -- Custom test: transaction amount must be positive or zero

select *
from {{ ref('fct_transactions_ml') }}
where amount < 0
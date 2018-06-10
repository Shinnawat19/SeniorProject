<template>
    <div class="item">
        <button type="button" class="btn" :class="{'btn-primary': action.action === 'BUY','btn-danger': action.action === 'SELL'}">{{action.action}}</button>
        <h6>{{ action.symbol }}</h6>
        <h6>{{ action.volume }}</h6>
        <h6>{{ action.averagePrice.toFixed(2) }}</h6>
        <h5>Date: {{ action.date | formateDate }}</h5>
        <hr>
    </div>
</template>

<script>
import moment from 'moment'
export default {
    props: {
        action: Object
    },
    filters: {
        formateDate(date) {
            if (date) {
                return moment(date).format('MM/DD/YYYY')
            }
        }
    }
}
</script>


<style scoped>
    .item {
        margin: 0 24px;
    }

    h6 {
        margin-left: 8px;
        display: inline;
    }

    h5 {
        font-size: 16px;
        margin-left: 70px;
        margin-bottom: 0;
    }

    hr {
        margin: 8px 0;
    }
</style>

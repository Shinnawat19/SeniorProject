<template>
    <div class="item">
        <button type="button" class="btn" :class="{'btn-primary': action.action === 'BUY','btn-danger': action.action === 'SELL'}">{{action.action}}</button>
        <h6>{{ action.symbol }}</h6>
        <h6>{{ action.volume }}</h6>
        <h6>{{ action.averagePrice.toFixed(2) }}</h6>
        <hr>
    </div>
</template>

<script>
export default {
    props: {
        action: Object
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
</style>

<template>
  <div id="app">
    <navbar></navbar>
    <div class="row margin-top-small">
      <div class="col-sm-3">
        <div class="item-block action">
          <h3 class="block-title">Action histories</h3>
          <div class="scrollable">
            <virtualList class="scroll" :size="40" :remain="8" :bench="32" :startIndex="0">
              <item  v-for="(action, index) in actions" :action="action" :key="index"></item>
            </virtualList>
          </div>
        </div>
      </div>
      <div class="col-sm-9">
        <div class="item-block capital">
          <h3 class="block-title">Capital Graph</h3>
          <div id="chartdiv" style="width: 100%; height: 250px;"></div>
        </div>
        <div class="item-block portfolio">
          <h3 class="block-title">Portfolio</h3>
          <table class="fixed_header">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Volume</th>
                <th>Average buy price</th>
                <th>Market price</th>
                <th>Profit</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(portfolio, index) in portfolios" :key="index">
                <td>{{portfolio.symbol}}</td>
                <td>{{portfolio.volume}}</td>
                <td>{{portfolio.averagePrice.toFixed(3)}}</td>
                <td>{{portfolio.marketPrice.toFixed(3)}}</td>
                <td>{{portfolio.profit.toFixed(3)}}</td> 
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Item from './Item.vue'
import Navbar from './Navbar'
import virtualList from 'vue-virtual-scroll-list'
import axios from 'axios'
import moment from 'moment'
export default {
  name: 'app',
  components: {
    item: Item,
    navbar: Navbar,
    virtualList
  },
  data() {
    return {
      data: [],
      charts: null,
      index: 0,
      actions: null,
      portfolios: null,
      botName: 'botname'
    }
  },
  created () {
    this.createChart()

    setInterval( async () => {
      await this.getTradeAction()
      await this.getPortfolio()
      await this.getCash()
    }, 5000)
  },
  methods: {
    getTradeAction() {
      axios.get('http://localhost:8000/trading/trade', {
        params: { name: this.botName }
      }).then(response => {
        this.actions = response.data.actions
      })
    },
    getPortfolio() {
      axios.get('http://localhost:8000/trading/portfolio', {
        params: { name: this.botName }
      }).then(response => {
        this.portfolios = response.data.portfolios
      })
    },
    getCash() {
      axios.get('http://localhost:8000/trading/capital', {
        params: { name: this.botName }
      }).then(response => {
        let date = moment(response.data.date).format('MM/DD/YYYY')
        this.data.push({"date": date, "value": response.data.capital})
        this.charts.validateData()
      })
    },
    createChart () {
      this.charts = AmCharts.makeChart("chartdiv",
      {
        "type": "serial",
        "theme": "light",
        "dataProvider": this.data,
        "valueAxes": [{
            "axisAlpha": 0,
            "position": "left"
        }],
        "graphs": [{
            "id":"g1",
            "balloonText": "[[category]]<br><b><span style='font-size:14px;'>[[value]]</span></b>",
            "bullet": "round",
            "bulletSize": 8,
            "lineColor": "#d1655d",
            "lineThickness": 2,
            "negativeLineColor": "#637bb6",
            "type": "smoothedLine",
            "valueField": "value"
        }],
        "chartCursor": {
            "categoryBalloonDateFormat": "DD/MM/YYYY",
            "cursorAlpha": 0,
            "valueLineEnabled":true,
            "valueLineBalloonEnabled":true,
            "valueLineAlpha":0.5,
            "fullWidth":true
        },
        "dataDateFormat": "DD/MM/YYYY",
        "categoryField": "date"
      }
    )
    }
  }
}
</script>
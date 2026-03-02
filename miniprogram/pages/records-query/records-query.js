var api = require('../../utils/api')

function formatDate(d) {
  var y = d.getFullYear()
  var m = ('0' + (d.getMonth() + 1)).slice(-2)
  var day = ('0' + d.getDate()).slice(-2)
  return y + '-' + m + '-' + day
}

Component({
  data: {
    date: '',
    rooms: [],
    roomNames: ['所有直播间'],
    roomIndex: 0,
    records: [],
    totalAdd: 0,
    totalSub: 0,
    loading: false,
    queried: false
  },
  lifetimes: {
    attached: function () {
      this.setData({ date: formatDate(new Date()) })
      this.loadRooms()
    }
  },
  methods: {
    loadRooms: function () {
      var that = this
      api.getRooms().then(function (rooms) {
        var names = ['所有直播间']
        rooms.forEach(function (r) { names.push(r.name) })
        that.setData({ rooms: rooms, roomNames: names })
      })
    },
    onDateChange: function (e) {
      this.setData({ date: e.detail.value })
    },
    onRoomChange: function (e) {
      this.setData({ roomIndex: parseInt(e.detail.value, 10) })
    },
    handleQuery: function () {
      var that = this
      var date = that.data.date
      var roomIndex = that.data.roomIndex
      var roomId = null
      if (roomIndex > 0) {
        roomId = that.data.rooms[roomIndex - 1].id
      }
      that.setData({ loading: true })
      api.getGlobalRecords(date, roomId).then(function (res) {
        that.setData({
          records: res.records,
          totalAdd: res.total_add,
          totalSub: res.total_sub,
          loading: false,
          queried: true
        })
      }).catch(function (err) {
        wx.showToast({ title: err.message || '查询失败', icon: 'none' })
        that.setData({ loading: false })
      })
    }
  }
})

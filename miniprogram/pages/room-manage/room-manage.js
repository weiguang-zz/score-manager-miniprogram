var api = require('../../utils/api')

Component({
  data: {
    rooms: [],
    newName: '',
    loading: false,
    editingId: null,
    editingName: ''
  },
  lifetimes: {
    attached: function () {
      this.loadRooms()
    }
  },
  methods: {
    loadRooms: function () {
      var that = this
      that.setData({ loading: true })
      api.getRooms().then(function (rooms) {
        that.setData({ rooms: rooms, loading: false })
      }).catch(function (err) {
        wx.showToast({ title: err.message || '加载失败', icon: 'none' })
        that.setData({ loading: false })
      })
    },
    onNewNameInput: function (e) {
      this.setData({ newName: e.detail.value })
    },
    handleAdd: function () {
      var that = this
      var name = that.data.newName.trim()
      if (!name) {
        wx.showToast({ title: '请输入直播间名称', icon: 'none' })
        return
      }
      api.createRoom(name).then(function () {
        that.setData({ newName: '' })
        that.loadRooms()
        wx.showToast({ title: '添加成功', icon: 'success' })
      }).catch(function (err) {
        wx.showToast({ title: err.message || '添加失败', icon: 'none' })
      })
    },
    startEdit: function (e) {
      var id = e.currentTarget.dataset.id
      var name = e.currentTarget.dataset.name
      this.setData({ editingId: id, editingName: name })
    },
    onEditNameInput: function (e) {
      this.setData({ editingName: e.detail.value })
    },
    handleSaveEdit: function () {
      var that = this
      var id = that.data.editingId
      var name = that.data.editingName.trim()
      if (!name) {
        wx.showToast({ title: '名称不能为空', icon: 'none' })
        return
      }
      api.updateRoom(id, name).then(function () {
        that.setData({ editingId: null, editingName: '' })
        that.loadRooms()
        wx.showToast({ title: '修改成功', icon: 'success' })
      }).catch(function (err) {
        wx.showToast({ title: err.message || '修改失败', icon: 'none' })
      })
    },
    cancelEdit: function () {
      this.setData({ editingId: null, editingName: '' })
    },
    handleDelete: function (e) {
      var that = this
      var id = e.currentTarget.dataset.id
      var name = e.currentTarget.dataset.name
      wx.showModal({
        title: '确认删除',
        content: '确定要删除直播间"' + name + '"吗？',
        confirmColor: '#ff4d4f',
        success: function (res) {
          if (res.confirm) {
            api.deleteRoom(id).then(function () {
              that.loadRooms()
              wx.showToast({ title: '已删除', icon: 'success' })
            }).catch(function (err) {
              wx.showToast({ title: err.message || '删除失败', icon: 'none' })
            })
          }
        }
      })
    }
  }
})

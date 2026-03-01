var api = require('../../utils/api')

Component({
  data: {
    allMembers: [],
    members: [],
    keyword: '',
    loading: false
  },
  lifetimes: {
    attached: function () {
      if (!api.isLoggedIn()) {
        wx.redirectTo({ url: '/pages/login/login' })
      }
    }
  },
  pageLifetimes: {
    show: function () {
      this.loadMembers()
    }
  },
  methods: {
    loadMembers: function () {
      var that = this
      that.setData({ loading: true })
      api.getMembers().then(function (members) {
        that.setData({ allMembers: members, loading: false })
        that.filterMembers()
      }).catch(function (err) {
        wx.showToast({ title: err.message || '加载失败', icon: 'none' })
        that.setData({ loading: false })
      })
    },
    onSearchInput: function (e) {
      this.setData({ keyword: e.detail.value })
      this.filterMembers()
    },
    onSearchClear: function () {
      this.setData({ keyword: '' })
      this.filterMembers()
    },
    filterMembers: function () {
      var keyword = this.data.keyword.trim().toLowerCase()
      if (!keyword) {
        this.setData({ members: this.data.allMembers })
        return
      }
      var filtered = this.data.allMembers.filter(function (m) {
        return m.name.toLowerCase().indexOf(keyword) !== -1
      })
      this.setData({ members: filtered })
    },
    goAddMember: function () {
      wx.navigateTo({ url: '/pages/add-member/add-member' })
    },
    goMemberDetail: function (e) {
      var id = e.currentTarget.dataset.id
      var name = e.currentTarget.dataset.name
      var score = e.currentTarget.dataset.score
      wx.navigateTo({
        url: '/pages/member/member?id=' + id + '&name=' + encodeURIComponent(name) + '&score=' + score
      })
    },
    exportAll: function () {
      api.downloadExport('/api/export/members')
    },
    handleLogout: function () {
      wx.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: function (res) {
          if (res.confirm) {
            api.logout()
          }
        }
      })
    }
  }
})

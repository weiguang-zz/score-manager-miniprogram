var BASE_URL = 'http://localhost:8000'

function getToken() {
  return wx.getStorageSync('token') || ''
}

function setToken(token) {
  wx.setStorageSync('token', token)
}

function clearToken() {
  wx.removeStorageSync('token')
}

function request(options) {
  return new Promise(function (resolve, reject) {
    wx.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getToken()
      },
      success: function (res) {
        if (res.statusCode === 401) {
          clearToken()
          wx.redirectTo({ url: '/pages/login/login' })
          reject(new Error('登录已过期'))
          return
        }
        if (res.statusCode >= 400) {
          var detail = res.data && res.data.detail
          reject(new Error(detail || '请求失败'))
          return
        }
        resolve(res.data)
      },
      fail: function (err) {
        reject(new Error(err.errMsg || '网络错误'))
      }
    })
  })
}

function login(username, password) {
  return request({
    url: '/api/auth/login',
    method: 'POST',
    data: { username: username, password: password }
  }).then(function (res) {
    setToken(res.access_token)
    return res
  })
}

function isLoggedIn() {
  return !!getToken()
}

function logout() {
  clearToken()
  wx.redirectTo({ url: '/pages/login/login' })
}

function getMembers() {
  return request({ url: '/api/members' })
}

function createMember(name, initialScore) {
  return request({
    url: '/api/members',
    method: 'POST',
    data: { name: name, initial_score: initialScore }
  })
}

function updateMember(id, name) {
  return request({
    url: '/api/members/' + id,
    method: 'PUT',
    data: { name: name }
  })
}

function deleteMember(id) {
  return request({
    url: '/api/members/' + id,
    method: 'DELETE'
  })
}

function getRecords(memberId) {
  return request({ url: '/api/members/' + memberId + '/records' })
}

function createRecord(memberId, changeAmount, reason) {
  return request({
    url: '/api/members/' + memberId + '/records',
    method: 'POST',
    data: { change_amount: changeAmount, reason: reason }
  })
}

function downloadExport(path) {
  var token = getToken()
  wx.request({
    url: BASE_URL + path,
    method: 'GET',
    responseType: 'arraybuffer',
    header: { 'Authorization': 'Bearer ' + token },
    success: function (res) {
      if (res.statusCode === 200) {
        var fs = wx.getFileSystemManager()
        var filePath = wx.env.USER_DATA_PATH + '/export_' + Date.now() + '.xlsx'
        fs.writeFile({
          filePath: filePath,
          data: res.data,
          encoding: 'binary',
          success: function () {
            wx.openDocument({
              filePath: filePath,
              fileType: 'xlsx',
              showMenu: true
            })
          },
          fail: function () {
            wx.showToast({ title: '保存失败', icon: 'error' })
          }
        })
      } else {
        wx.showToast({ title: '导出失败', icon: 'error' })
      }
    },
    fail: function () {
      wx.showToast({ title: '下载失败', icon: 'error' })
    }
  })
}

module.exports = {
  login: login,
  isLoggedIn: isLoggedIn,
  logout: logout,
  getMembers: getMembers,
  createMember: createMember,
  updateMember: updateMember,
  deleteMember: deleteMember,
  getRecords: getRecords,
  createRecord: createRecord,
  downloadExport: downloadExport
}

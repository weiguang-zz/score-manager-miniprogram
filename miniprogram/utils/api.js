var BASE_URL = 'https://score-manager.umember.cn'

function getToken() {
  return wx.getStorageSync('token') || ''
}

function setToken(token) {
  wx.setStorageSync('token', token)
}

function clearToken() {
  wx.removeStorageSync('token')
}

function setRole(role) {
  wx.setStorageSync('role', role)
}

function getRole() {
  return wx.getStorageSync('role') || 'admin'
}

function setUsername(username) {
  wx.setStorageSync('username', username)
}

function getUsername() {
  return wx.getStorageSync('username') || ''
}

function isAdmin() {
  return getRole() === 'admin'
}

function canEdit() {
  var role = getRole()
  return role === 'admin' || role === 'staff_editor'
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
    setRole(res.role)
    setUsername(res.username)
    return res
  })
}

function isLoggedIn() {
  return !!getToken()
}

function logout() {
  clearToken()
  wx.removeStorageSync('role')
  wx.removeStorageSync('username')
  wx.redirectTo({ url: '/pages/login/login' })
}

function getUserInfo() {
  return request({ url: '/api/auth/me' })
}

function changePassword(oldPassword, newPassword) {
  return request({
    url: '/api/auth/change-password',
    method: 'POST',
    data: { old_password: oldPassword, new_password: newPassword }
  })
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

function createRecord(memberId, changeAmount, reason, roomId) {
  var data = { change_amount: changeAmount, reason: reason }
  if (roomId) { data.room_id = roomId }
  return request({
    url: '/api/members/' + memberId + '/records',
    method: 'POST',
    data: data
  })
}

// Staff management
function getStaffList() {
  return request({ url: '/api/staff' })
}

function createStaff(username, password, role) {
  return request({
    url: '/api/staff',
    method: 'POST',
    data: { username: username, password: password, role: role }
  })
}

function updateStaff(staffId, role) {
  return request({
    url: '/api/staff/' + staffId,
    method: 'PUT',
    data: { role: role }
  })
}

function deleteStaff(staffId) {
  return request({
    url: '/api/staff/' + staffId,
    method: 'DELETE'
  })
}

function downloadExport(path, startDate, endDate) {
  var token = getToken()
  var url = BASE_URL + path
  var params = []
  if (startDate) { params.push('start_date=' + startDate) }
  if (endDate) { params.push('end_date=' + endDate) }
  if (params.length > 0) { url = url + '?' + params.join('&') }

  wx.request({
    url: url,
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

// Room management
function getRooms() {
  return request({ url: '/api/rooms' })
}

function createRoom(name) {
  return request({
    url: '/api/rooms',
    method: 'POST',
    data: { name: name }
  })
}

function updateRoom(id, name) {
  return request({
    url: '/api/rooms/' + id,
    method: 'PUT',
    data: { name: name }
  })
}

function deleteRoom(id) {
  return request({
    url: '/api/rooms/' + id,
    method: 'DELETE'
  })
}

// Global records query
function getGlobalRecords(date, roomId) {
  var url = '/api/records?date=' + date
  if (roomId) { url = url + '&room_id=' + roomId }
  return request({ url: url })
}

module.exports = {
  login: login,
  isLoggedIn: isLoggedIn,
  logout: logout,
  getUserInfo: getUserInfo,
  getRole: getRole,
  getUsername: getUsername,
  isAdmin: isAdmin,
  canEdit: canEdit,
  changePassword: changePassword,
  getMembers: getMembers,
  createMember: createMember,
  updateMember: updateMember,
  deleteMember: deleteMember,
  getRecords: getRecords,
  createRecord: createRecord,
  getStaffList: getStaffList,
  createStaff: createStaff,
  updateStaff: updateStaff,
  deleteStaff: deleteStaff,
  downloadExport: downloadExport,
  getRooms: getRooms,
  createRoom: createRoom,
  updateRoom: updateRoom,
  deleteRoom: deleteRoom,
  getGlobalRecords: getGlobalRecords
}

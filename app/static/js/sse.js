//  vue实例
var vm = new Vue ({
    el: '#out',
    // 自定义定界符，避免vue定界符与jinja2冲突，改变vue起始定界
    delimiters: ['@{', '}}'],
    // 实例属性
    data: {
        items: []
    },
    mounted() {
        // 监听服务端消息
        sse()
    }
})

// 通过EventSource对象与后端建立连接
function sse() {
    var source = new EventSource('/stream')
    // 监听消息事件（与nodejs用data事件sock流
    source.onmessage = function (e) {
        // XSS in chat is fun
        // 动态渲染页面（代理vue实例数据操作）
        vm.$data.items.push(e.data)
    }
}

// ajax与后端交互，向服务端发送消息
$('#in').keyup(function (e) {
   // 回车keycode为13
    if (e.keyCode == 13) {
        $.post('/chatpost', { 'message': $(this).val() })
        $(this).val('')
    }
})

// 自动消失闪现
$(document).ready(function () {
    setTimeout(() => {
        $(".flashes").fadeOut(3000);
    })
})

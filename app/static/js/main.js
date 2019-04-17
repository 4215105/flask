// JavaScript Document

// variables for the Shuffling figures
var count = 0;		// 计数：确定当前应该是第几张图片显示（count = 0, 1, 2, ..., (n-1)）
var isgo = false;
/*
	确定向左滑动还是向右滑动
	1) isgo = true
		一连串图片向左滑动
	2) isgo = false
		一连串图片向右滑动
*/
var timer;			// 计时器

window.onload = function(){
	var ul_img = document.getElementsByClassName("ul_img")[0];	// 获取包含图片的容器
	var li_img = document.getElementsByClassName("li_img");		// 获取那一串图片
	var div_btn = document.getElementsByClassName("div_btn");	// 获取那一串按钮

	div_btn[0].style.boxShadow = "3px 3px 6px #4c4c4c";			// 对其一个按钮做添加阴影处理

	showtime();	// 开始计时

	// 当轮播图顺序滑动时
	function showtime(){
		timer = setInterval(function(){
			if(isgo === false){
				console.log(count);
				if(count >= li_img.length - 2){
					count = li_img.length - 1;
					isgo = true;
				}else{
					count++;
				}
				ul_img.style.transform = "translate(" + -500 * count + "px)";	// 注意到这里的500了吗？这是每次滑动的距离
			}else{
				count--;
				ul_img.style.transform = "translate(" + -500 * count + "px)";
				if(count <= 0){
					count = 0;
					isgo = false;
				}
			}	// 选择显示的图片，“去到哪里”

	        for(var i = 0; i < div_btn.length; ++i){
	            div_btn[i].style.boxShadow = "none";
			}	// 现将所有按钮恢复原状
			div_btn[count].style.boxShadow = "3px 3px 6px #4c4c4c";	// 再对应图片的按钮做阴影处理
	    }, 4000);	// 规定每4秒换一次
	}

	// 当鼠标放在对应的按钮上时，马上去到对应的图片
	for(var b = 0; b < div_btn.length; ++b){
		div_btn[b].index = b;
		// 当鼠标放在按钮上时，要停止计时
		div_btn[b].onmouseover = function(){

			clearInterval(timer);

			for(var a = 0; a < div_btn.length; a++){
				div_btn[a].style.boxShadow = "none";
			}
			div_btn[this.index].style.boxShadow = "3px 3px 6px #4c4c4c";

			if(this.index === li_img.length - 1){
				isgo = true;
			}
			if(this.index === 0){
				isgo = false;
			}
			count = this.index;
			ul_img.style.transform = "translate(" + -500 * count + "px)";

		};
		// 当鼠标移开时，继续计时
		div_btn[b].onmouseout = function(){
			showtime();
		};
	}
};

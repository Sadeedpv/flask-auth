window.onload = () => {
    edit();
    observing();
}

function edit(){
    var content = document.querySelector('.edit');
    lst = [['B', 'u', 'y '], ['S', 'e', 'l', 'l'], ['E', 'n', 'j', 'o', 'y'],['R', 'e', 'l', 'a', 'x']]
    let j = 0;
    let i = 0;


    setInterval(() => {
        content.innerHTML += lst[i][j];
        j++;
        if (j > lst[i].length){
            i++;
            content.innerHTML = ''
            j = 0;
        }
        if (i >= lst.length){
            content.innerHTML = '';
            i = 0;
            j = 0;            
        }

    }, 500)

}


window.onscroll = () => {
    if (window.innerWidth > 1280){
        navcolor();

    }

}

function navcolor(){
    var nav = document.querySelector('.remain-flex')
    var nav2 = document.querySelector('.navbar');
    var hero = document.querySelector('.hero');
 

    if (document.body.scrollTop >= hero.clientHeight/15 || document.documentElement.scrollTop >= hero.clientHeight/15){
        nav2.setAttribute('style', 'background-color : white !important')
        nav.setAttribute('style', 'background-color : white !important')
        nav.style.height = nav2.style.height;
    }else{
        nav2.setAttribute('style', 'background-color : transparent !important')
        nav.setAttribute('style', 'background-color : transparent !important')

        
    }
    
}

function observing(){
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting){
                document.querySelectorAll('.para')[0].style.opacity = "1";
                document.querySelectorAll('.para')[1].style.opacity = "1";
                document.querySelectorAll('.para')[2].style.opacity = "1";
                document.querySelectorAll('.para')[3].style.opacity = "1";
                document.querySelectorAll('.text-1')[0].style.transform = "translateX(0%)";
                document.querySelectorAll('.text-1')[1].style.transform = "translateX(0%)";
                document.querySelectorAll('.text-2')[0].style.transform = "translateX(0%)";
                document.querySelectorAll('.text-2')[1].style.transform = "translateX(0%)";
            }
        })
    })
    
    observer.observe(document.querySelector('.observe'))
}


function display(){
    document.querySelectorAll('.hid-forgot').forEach((e) =>{
        e.style.display = "unset"
    })
}

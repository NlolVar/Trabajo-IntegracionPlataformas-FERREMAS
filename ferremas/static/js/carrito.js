var actuBotones = document.getElementsByClassName('update-cart')

for (i = 0; i < actuBotones.length; i++) {
	actuBotones[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)
        console.log('USER:', user)
		
        if (user == 'AnonymousUser'){
            addCookieItem(productId, action)
			console.log('User is not authenticated')
			
		}else{
            updateUserOrder(productId, action)
		}
	})
}

function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')
    var url = '/update_item/'
    console.log('URL:', url)
    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken
        },
        body:JSON.stringify({'productId':productId, 'action':action})
    })
    .then((response) => {
        return response.json();
    })
    .then((data) =>{
        location.reload()
    })
}

function addCookieItem(productId, action){
    console.log("Usuario no esta autenticado")

    if (action == 'add'){
        if (carrito[productId] == undefined){
            carrito[productId] = {'cantidad': 1}
        }else{
            carrito[productId]['cantidad'] += 1
        }
    }

    if (action == 'remove'){
        carrito[productId]['cantidad'] -= 1
        
        if (carrito[productId]['cantidad'] <= 0){
            console.log('Item debio haber sido eliminado')
            delete carrito[productId];
        }
    }
    console.log('carrito:', carrito)
    document.cookie= 'carrito='+ JSON.stringify(carrito) + ";domain=;path=/"

    location.reload()
}
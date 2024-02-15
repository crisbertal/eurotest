# Requisitos Funcionales
## Lobby
- Solo hay un unico lobby donde conectarse con WebSockets

## Usuarios
Existen dos perfiles de jugador
- Admin
    - El admin es un jugador mas
    - La unica diferencia es que el admin puede cambiar el pais que esta actuando para que se pueda votar
- Jugador
    - Solo vota
    - Visualiza las votaciones

## Votos
*POR DEFINIR*
- Se puede votar mas de una vez por cambio de opinion o lo votado va a misa? #definir
- Se puede votar durante la actuacion 
- Se puede volver a una actuacion anterior y cambiar de opinion? #definir
- Opciones posibles de voto #definir:
    - Votar de 1 al 10 en todas las actuaciones
    - Votar de 1 a _n_actuaciones_. Como si fuera el concurso, por ejemplo, si hay 20 paises puedes usar el voto del 1 al 20. Si votas con 1 a Espana no puedes volver a votar con 1 a Alemania. Alemania tendria que ser de 2 para arriba. La suma de los votos sera lo que determine el ranking
- Que se votaria por pais?
    - Sonido
    - Performance
    - Er meme
    - Posibilidades reales de que gane
    - *O se vota con un valor en general y ya?*
- Lo de que el voto sea anonimo o no #definir
- hacemos que si se vota con la puntuacion maxima saca una notificacion dorada? #definir 

## Login
- El login se hace solo con username para simplificar el proceso (esto lo podemos cambiar si queremos) #definir
- La session se guarda permanente en el navegador por si se cierra y abre el navegador que pueda volver a donde estaba. 
- Si no, bastaria con volver a poner el mismo nombre de usuario anterior. 


# User Story
1. Usuario se loguea insertando el nombre de usuario. 
2. En la aplicacion se muestran dos paneles:
    - Panel actuacion en proceso: aqui es donde puedes votar. 
    - Ranking: ver las estadisticas de actuaciones anteriores. 
3. Mientras este un pais actuando, el usuario puede votar. 
4. Al terminar la actuacion se dejara un tiempo de disputa entre los jugadores. 
5. Al iniciar la siguiente actuacion, el admin cambiara el pais que esta actuando y se resetean los votos
6. Al terminar todas las actuaciones, el panel de actuacion en proceso quedara vacio y no se podra votar nada
7. Solo quedara activo el ranking de lo votado para consulta.


# Requisitos no funcionales
- El despliegue se hara con Docker y docker-compose
- La base de datos sera relacional
- El backend se hara con Quart en python
- El fron a decidir (React?) #definir
- Hay dos opciones de despliegue: #definir
    - En local y los conectados a la misma wifi pueden jugar (habria que levantar una VPN para que los de fuera pueda entrar tambien, por ejemplo, Hamachi)
    - Vamos full pro y compramos un dominio y hosting (<3) 



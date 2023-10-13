import os
from flask import Flask, request, redirect
import base64
import numpy as np
from keras.models import load_model
from io import BytesIO
from PIL import Image
from io import BytesIO
from skimage.transform import resize

app = Flask(__name__)

# Cargar el modelo entrenado
modelo = load_model('my_model.h5')

main_html = """
<html>
<head></head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;

  function InitThis() {
      ctx = document.getElementById('myCanvas').getContext("2d");
      document.getElementById('mensaje').innerHTML  = '';
      document.getElementById('numero').value = '';  // Elimina la sugerencia inicial

      $('#myCanvas').mousedown(function (e) {
          mousePressed = true;
          Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, false);
      });

      $('#myCanvas').mousemove(function (e) {
          if (mousePressed) {
              Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, true);
          }
      });

      $('#myCanvas').mouseup(function (e) {
          mousePressed = false;
      });
      $('#myCanvas').mouseleave(function (e) {
          mousePressed = false;
      });
  }

  function Draw(x, y, isDown) {
      if (isDown) {
          ctx.beginPath();
          ctx.strokeStyle = 'black';
          ctx.lineWidth = 11;
          ctx.lineJoin = "round";
          ctx.moveTo(lastX, lastY);
          ctx.lineTo(x, y);
          ctx.closePath();
          ctx.stroke();
      }
      lastX = x; lastY = y;
  }

  function clearArea() {
      // Restablece el lienzo limpiando el dibujo
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

function prepareImg() {
    var canvas = document.getElementById('myCanvas');
    var imgData = canvas.toDataURL('image/png');
    document.getElementById('myImage').value = imgData;

    // Actualizar el mensaje a "Enviando..."
    document.getElementById('mensaje').innerHTML = 'Enviando...';

    // Realizar una solicitud AJAX para enviar la imagen
    var formData = new FormData(document.forms[0]);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = xhr.responseText;
            document.getElementById('mensaje').innerHTML = response;  // Actualizar el mensaje con la respuesta del servidor
        }
    };
    xhr.send(formData);

    return false;
}


</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript"></script>
    <div align="left">
      <img src="https://upload.wikimedia.org/wikipedia/commons/f/f7/Uni-logo_transparente_granate.png" width="300"/>
    </div>
    <div align="rigth">
        <h2>Instrucciones</h2>
        <p> 1. Dibujar el simbolo en el cuadrado </p>
        <p> 2. Precionar "enviar" </p>
        <p> 3. Te redirigira a una pagina "upload" donde mostrara el nombre del simbolo seleccionado </p>
        <p> 4. Retroceder, para volver a dibujar otro simbolo </p>
        <p> 5. Repite los pasos del 1 al 5 </p>



        
    </div>
    <div align="center">
        <h1 id="mensaje"></h1>
        <canvas id="myCanvas" width="200" height="200" style="border:2px solid black"></canvas>
        <br/>
        <br/>
        <button onclick="javascript:clearArea();return false;">Borrar</button>
    </div>
    <div align="center">
      <form method="post" action="upload" onsubmit="javascript:prepareImg();"  enctype="multipart/form-data">
      <input id="numero" name="numero" type="hidden" value="">
      <input id="myImage" name="myImage" type="hidden" value="">
      <input id="bt_upload" type="submit" value="Enviar">
      </form>
    </div>
</body>
</html>

"""

@app.route("/")
def main():
    return main_html

@app.route('/upload', methods=['POST'])
def upload():
    try:
        img_data = request.form.get('myImage').replace(
            "data:image/png;base64,", "")
        img_data = base64.b64decode(img_data)

        # Convertir los datos de la imagen a un objeto PIL Image
        img = Image.open(BytesIO(img_data))

        # Crear un fondo blanco RGBA
        white_img = Image.new('RGBA', img.size, 'WHITE')

        # Pegar la imagen en el fondo blanco
        img = Image.alpha_composite(white_img, img)
        img = img.convert('L')
        img = np.array(img)/255.0

        img = resize(img, (28, 28))

        img = img.reshape((28, 28, 1))

        img = 1 - img

        result = modelo.predict(img[None, :, :, :])[0]

        print("Resultado:", result)
        predicted_class = np.argmax(result, axis=0)
        print("Clase predicha:", predicted_class)

        # Mapeo de clases a nombres
        class_names = ["pi", "beta", "gamma", "delta", "epsilon"]
        predicted_symbol = class_names[predicted_class]

        # Devolver el resultado
        return f"El símbolo reconocido es: {predicted_symbol}"

    except Exception as err:
        print("Ocurrió un error")
        print(err)

    return redirect("/", code=302)

if __name__ == "__main__":
    digits = ["pi", "beta", "gamma", "delta", "epsilon"]
    for d in digits:
        if not os.path.exists(str(d)):
            os.mkdir(str(d))
    app.run()
#
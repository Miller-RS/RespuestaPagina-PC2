import tempfile
import os
from flask import Flask, request, redirect, send_file, jsonify
from skimage import io
import base64
import glob
import numpy as np
from keras.models import load_model
from keras.preprocessing import image
from io import BytesIO

app = Flask(__name__)

# Cargar el modelo entrenado
modelo = load_model('modelo_entrenado.h5')

main_html = """
<html>
<head></head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;

   function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
   }

  function InitThis() {
      ctx = document.getElementById('myCanvas').getContext("2d");


      numero = getRndInteger(0, 10);
      letra = ["pi", "beta", "gamma", "delta", "epsilon"];
      random = Math.floor(Math.random() * letra.length);
      aleatorio = letra[random];

      document.getElementById('mensaje').innerHTML  = 'Dibujando un ' + aleatorio;
      document.getElementById('numero').value = aleatorio;

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
      // Use the identity matrix while clearing the canvas
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  //https://www.askingbox.com/tutorial/send-html5-canvas-as-image-to-server
function prepareImg() {
    var canvas = document.getElementById('myCanvas');
    var imgData = canvas.toDataURL('image/png'); // Genera la imagen en formato PNG
    document.getElementById('myImage').value = imgData;
}




</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript" ></script>
    <div align="left">
      <img src="https://upload.wikimedia.org/wikipedia/commons/f/f7/Uni-logo_transparente_granate.png" width="300"/>
    </div>
    <div align="center">
        <h1 id="mensaje">Dibujando...</h1>
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
        img_data = request.form.get('myImage').replace("data:image/png;base64,","")
        aleatorio = request.form.get('numero')

        # Guardar la imagen
        with tempfile.NamedTemporaryFile(delete=False, mode="w+b", suffix='.png', dir=str(aleatorio)) as fh:
            fh.write(base64.b64decode(img_data))

        # Cargar la imagen y realizar la predicción
        img = image.load_img(fh.name, target_size=(200, 200))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)

        # Realizar la predicción
        result = modelo.predict(img_array)
        predicted_class = np.argmax(result)

        # Mapa de clases a nombres
        class_names = ["pi", "beta", "gamma", "delta", "epsilon"]
        predicted_symbol = class_names[predicted_class]

        # Devolver el resultado
        return f"El símbolo reconocido es: {predicted_symbol}"

    except Exception as err:
        print("Error occurred")
        print(err)

    return redirect("/", code=302)

# Resto del código igual

if __name__ == "__main__":
    digits = ["pi", "beta", "gamma", "delta", "epsilon"]
    for d in digits:
        if not os.path.exists(str(d)):
            os.mkdir(str(d))
    app.run()

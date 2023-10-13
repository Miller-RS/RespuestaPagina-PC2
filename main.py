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
from PIL import Image
from skimage.color import rgb2gray
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from io import BytesIO
from imageio import imread
from skimage.transform import resize
#import cv2

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
      document.getElementById('mensaje').innerHTML  = 'Dibujando...';
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
      // Use the identity matrix while clearing the canvas
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
    xhr.open("POST", "upload", true);
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
        # #aleatorio = request.form.get('numero')
        img_data = base64.b64decode(img_data)

        # Convert the image data to a PIL Image object
        img = Image.open(BytesIO(img_data))

        print("flag1")
        # Guardar la imagen
        # with tempfile.NamedTemporaryFile(delete=False, mode="w+b", suffix='.png', dir=str(aleatorio)) as fh:
        #      fh.write(base64.b64decode(img_data))

        print("flag2")
        
        white_img = Image.new('RGBA', img.size, 'WHITE')  # Create a white rgba background

        # Paste the image file on the white image
        img = Image.alpha_composite(white_img, img)
        img = img.convert('L')
        img = np.array(img)/255.0
       
        print("data type ", img.dtype)
        print("minimo maximo ",img.min(), img.max())
    
        plt.imshow(img , cmap='gray' )
        plt.show()
        
        print("flag2.1")
        #img = np.invert(img)
        # plt.imshow(img , cmap='gray' )
        # plt.show()
        print("flag2.2")
        img = resize(img, (28, 28))
        plt.imshow(img, cmap='gray')
        plt.show()
        print("flag2.3")
        img = img.reshape((1, 28, 28, 1))
        print("flag2.4")
        ##################################

        
        plt.imshow(img[0,:,:,0] )
        plt.show()
        print(type(img))
        print(img.shape)
        print(len(img))
        print("contenido ",img.size)

        #img = img/255

        result = modelo.predict(img[None,:,:,:])[0]
        #result = modelo.predict(img)

        print("Result:", result)
        predicted_class = np.argmax(result,axis=1)
        print("Predicted class:", predicted_class)

        # Mapa de clases a nombres
        class_names = ["pi", "beta", "gamma", "delta", "epsilon"]
        predicted_symbol = class_names[predicted_class]

        # Devolver el resultado
        return f"El símbolo reconocido es: {predicted_symbol}"

    except Exception as err:
        print("Error occurred")
        print(err)

    return redirect("/", code=302)

if __name__ == "__main__":
    digits = ["pi", "beta", "gamma", "delta", "epsilon"]
    for d in digits:
        if not os.path.exists(str(d)):
            os.mkdir(str(d))
    app.run()

#
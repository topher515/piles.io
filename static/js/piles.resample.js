/**
*
*  Base64 encode / decode
*  http://www.webtoolkit.info/
*
**/
 
var Base64 = {
 
	// private property
	_keyStr : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
 
	// public method for encoding
	encode : function (input) {
		var output = "";
		var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
		var i = 0;
 
		input = Base64._utf8_encode(input);
 
		while (i < input.length) {
 
			chr1 = input.charCodeAt(i++);
			chr2 = input.charCodeAt(i++);
			chr3 = input.charCodeAt(i++);
 
			enc1 = chr1 >> 2;
			enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
			enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
			enc4 = chr3 & 63;
 
			if (isNaN(chr2)) {
				enc3 = enc4 = 64;
			} else if (isNaN(chr3)) {
				enc4 = 64;
			}
 
			output = output +
			this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
			this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);
 
		}
 
		return output;
	},
 
	// public method for decoding
	decode : function (input) {
		var output = "";
		var chr1, chr2, chr3;
		var enc1, enc2, enc3, enc4;
		var i = 0;
 
		input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
 
		while (i < input.length) {
 
			enc1 = this._keyStr.indexOf(input.charAt(i++));
			enc2 = this._keyStr.indexOf(input.charAt(i++));
			enc3 = this._keyStr.indexOf(input.charAt(i++));
			enc4 = this._keyStr.indexOf(input.charAt(i++));
 
			chr1 = (enc1 << 2) | (enc2 >> 4);
			chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
			chr3 = ((enc3 & 3) << 6) | enc4;
 
			output = output + String.fromCharCode(chr1);
 
			if (enc3 != 64) {
				output = output + String.fromCharCode(chr2);
			}
			if (enc4 != 64) {
				output = output + String.fromCharCode(chr3);
			}
 
		}
 
		output = Base64._utf8_decode(output);
 
		return output;
 
	},
 
	// private method for UTF-8 encoding
	_utf8_encode : function (string) {
		string = string.replace(/\r\n/g,"\n");
		var utftext = "";
 
		for (var n = 0; n < string.length; n++) {
 
			var c = string.charCodeAt(n);
 
			if (c < 128) {
				utftext += String.fromCharCode(c);
			}
			else if((c > 127) && (c < 2048)) {
				utftext += String.fromCharCode((c >> 6) | 192);
				utftext += String.fromCharCode((c & 63) | 128);
			}
			else {
				utftext += String.fromCharCode((c >> 12) | 224);
				utftext += String.fromCharCode(((c >> 6) & 63) | 128);
				utftext += String.fromCharCode((c & 63) | 128);
			}
 
		}
 
		return utftext;
	},
 
	// private method for UTF-8 decoding
	_utf8_decode : function (utftext) {
		var string = "";
		var i = 0;
		var c = c1 = c2 = 0;
 
		while ( i < utftext.length ) {
 
			c = utftext.charCodeAt(i);
 
			if (c < 128) {
				string += String.fromCharCode(c);
				i++;
			}
			else if((c > 191) && (c < 224)) {
				c2 = utftext.charCodeAt(i+1);
				string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
				i += 2;
			}
			else {
				c2 = utftext.charCodeAt(i+1);
				c3 = utftext.charCodeAt(i+2);
				string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
				i += 3;
			}
 
		}
 
		return string;
	}
 
}


var Resample = (function (canvas) {

 // (C) WebReflection Mit Style License

 // Resample function, accepts an image
 // as url, base64 string, or Image/HTMLImgElement
 // optional width or height, and a callback
 // to invoke on operation complete
 function Resample(img, width, height, onresample) {
  var
   // check the image type
   load = typeof img == "string",
   // Image pointer
   i = load || img
  ;
  // if string, a new Image is needed
  if (load) {
   i = new Image;
   // with propers callbacks
   i.onload = onload;
   i.onerror = onerror;
  }
  // easy/cheap way to store info
  i._onresample = onresample;
  i._width = width;
  i._height = height;
  // if string, we trust the onload event
  // otherwise we call onload directly
  // with the image as callback context
  load ? (i.src = img) : onload.call(img);
 }
 
 // just in case something goes wrong
 function onerror() {
  throw ("not found: " + this.src);
 }
 
 // called when the Image is ready
 function onload() {
  var
   // minifier friendly
   img = this,
   // the desired width, if any
   width = img._width,
   // the desired height, if any
   height = img._height,
   // the callback
   onresample = img._onresample
  ;
  // if width and height are both specified
  // the resample uses these pixels
  // if width is specified but not the height
  // the resample respects proportions
  // accordingly with orginal size
  // same is if there is a height, but no width
  width == null && (width = round(img.width * height / img.height));
  height == null && (height = round(img.height * width / img.width));
  // remove (hopefully) stored info
  delete img._onresample;
  delete img._width;
  delete img._height;
  // when we reassign a canvas size
  // this clears automatically
  // the size should be exactly the same
  // of the final image
  // so that toDataURL ctx method
  // will return the whole canvas as png
  // without empty spaces or lines
  canvas.width = width;
  canvas.height = height;
  // drawImage has different overloads
  // in this case we need the following one ...
  context.drawImage(
   // original image
   img,
   // starting x point
   0,
   // starting y point
   0,
   // image width
   img.width,
   // image height
   img.height,
   // destination x point
   0,
   // destination y point
   0,
   // destination width
   width,
   // destination height
   height
  );
  // retrieve the canvas content as
  // base4 encoded PNG image
  // and pass the result to the callback
  var pngDataURL = canvas.toDataURL('image/png')
  
  if (canvas.toBlob) {
      // If the `toBlob` method is implemented in this browser then use that
      canvas.toBlob(function(pngBlob) {
          onresample(pngDataURL,pngBlob)
      })
  } else {
      // Otherwise build the blob yourself
      Blobber = WebKitBlobBuilder || MozBlobBuilder;
      blobber = new Blobber();
      //b64data = pngDataURL.slice(pngDataURL.search('base64,')+7)
      //var a = Base64.decode(b64data)   //window.atob(b64data)
      blobber.append(pngDataURL); //a);
      onresample(pngDataURL,blobber.getBlob('image/png'));
  }
  
 }
 
 var
  // point one, use every time ...
  context = canvas.getContext("2d"),
  // local scope shortcut
  round = Math.round
 ;
 
 return Resample;
 
}(
 // lucky us we don't even need to append
 // and render anything on the screen
 // let's keep this DOM node in RAM
 // for all resizes we want
 this.document.createElement("canvas"))
);
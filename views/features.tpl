%from api import Store #public_get_url
%from utils import human_size
%from settings import settings

%def head():
<script src="http://{{settings('CONTENT_DOMAIN')}}/static/js/resample.js" type="text/javascript">
<script>
$(function() {
    
    
    
});
</script>
%end

%def content():
<div class="container" style="z-index:600;">
<div class="content" style="position:relative;">
	
	<img style="position:absolute; top:-90px; right:-30px; opacity:.1;" src="http://{{settings('CONTENT_DOMAIN')}}/static/img/pile_256.png"  />
	<h1 style="margin: 25px inherit 0px inherit">Feedback</h1>
	%if feedbacks.count() == 0:
	<div>
		<h6>Nobody has left any feedback.</h6>
	</div>
	%else:
	
	<h6>These messages were left by other Alpha testers.</h6>
	<table id="pub-files" class="tablesorter zebra-striped">
		<thead>
			<tr>
				<th></th><th>Email</th><th>Message</th><th>When</th>
			</tr>
		</thead>
		%for feedback in feedbacks:
		<tbody>
			<tr>
				<td>
				    %if feedback['type'] == 'dislike':
				        <img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/thumb_dislike_big.png" height="64"/>
				    %elif feedback['type'] == 'bug':
    				    <img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/bug_big.png" height="64"/>
				    %else:
        			    <img src="http://{{settings('CONTENT_DOMAIN')}}/static/img/thumb_like_big.png" height="64"/>
				    %end
				</td>
				<td>{{feedback.get('email') or 'Anonymous'}}</td>
				<td>{{feedback['message']}}</td>
				<td>{{feedback['datetime'].strftime('%Y-%m-%d %H:%M:%S')}}</td>
			</tr>
		</tbody>
		%end
	</table>
	%end
	
	
	<input id="width" type="text" value="320">
	<input id="height" type="text" value="">
	<input id="file" type="file" value="">
	<span id="message" ></span>
	<div id="img"></div>
	
	<script>
	(function (global, $width, $height, $file, $message, $img) {

     // (C) WebReflection Mit Style License

     // simple FileReader detection
     if (!global.FileReader)
      // no way to do what we are trying to do ...
      return $message.innerHTML = "FileReader API not supported"
     ;

     // async callback, received the
     // base 64 encoded resampled image
     function resampled(data) {
      $message.innerHTML = "done";
      ($img.lastChild || $img.appendChild(new Image)
      ).src = data;
     }

     // async callback, fired when the image
     // file has been loaded
     function load(e) {
      $message.innerHTML = "resampling ...";
      // see resample.js
      Resample(
        this.result,
        this._width || null,
        this._height || null,
        resampled
      );

     }

     // async callback, fired if the operation
     // is aborted ( for whatever reason )
     function abort(e) {
      $message.innerHTML = "operation aborted";
     }

     // async callback, fired
     // if an error occur (i.e. security)
     function error(e) {
      $message.innerHTML = "Error: " + (this.result || e);
     }

     // listener for the input@file onchange
     $file.addEventListener("change", function change() {
      var
       // retrieve the width in pixel
       width = parseInt($width.value, 10),
       // retrieve the height in pixels
       height = parseInt($height.value, 10),
       // temporary variable, different purposes
       file
      ;
      // no width and height specified
      // or both are NaN
      if (!width && !height) {
       // reset the input simply swapping it
       $file.parentNode.replaceChild(
        file = $file.cloneNode(false),
        $file
       );
       // remove the listener to avoid leaks, if any
       $file.removeEventListener("change", change, false);
       // reassign the $file DOM pointer
       // with the new input text and
       // add the change listener
       ($file = file).addEventListener("change", change, false);
       // notify user there was something wrong
       $message.innerHTML = "please specify width or height";
      } else if(
       // there is a files property
       // and this has a length greater than 0
       ($file.files || []).length &&
       // the first file in this list 
       // has an image type, hopefully
       // compatible with canvas and drawImage
       // not strictly filtered in this example
       /^image\//.test((file = $file.files[0]).type)
      ) {
       // reading action notification
       $message.innerHTML = "reading ...";
       // create a new object
       file = new FileReader;
       // assign directly events
       // as example, Chrome does not
       // inherit EventTarget yet
       // so addEventListener won't
       // work as expected
       file.onload = load;
       file.onabort = abort;
       file.onerror = error;
       // cheap and easy place to store
       // desired width and/or height
       file._width = width;
       file._height = height;
       // time to read as base 64 encoded
       // data te selected image
       file.readAsDataURL($file.files[0]);
       // it will notify onload when finished
       // An onprogress listener could be added
       // as well, not in this demo tho (I am lazy)
      } else if (file) {
       // if file variable has been created
       // during precedent checks, there is a file
       // but the type is not the expected one
       // wrong file type notification
       $message.innerHTML = "please chose an image";
      } else {
       // no file selected ... or no files at all
       // there is really nothing to do here ...
       $message.innerHTML = "nothing to do";
      }
     }, false);
    }(
     // the global object
     this,
     // all required fields ...
     document.getElementById("width"),
     document.getElementById("height"),
     document.getElementById("file"),
     document.getElementById("message"),
     document.getElementById("img")
    ));
    </script>
	
	
</div>

</div>
%end

%rebase layout content=content, head=head, meta={'title':'Features'}
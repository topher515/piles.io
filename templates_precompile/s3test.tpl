
%def head():

%end

%def content():
<script>
$(function(){
    $('#swfupload-control').swfupload({
        // Backend Settings
        upload_url: "http://piles-dev.s3.amazonaws.com/",    // Relative to the SWF file (or you can use absolute paths)
			  http_success : [ 200, 201, 204 ], 		// FOR AWS
    
        use_query_strings: false,
    
        // File Upload Settings
        file_size_limit : "102400", // 100MB
        file_types : "*.*",
        file_types_description : "All Files",
        file_upload_limit : "10",
        file_queue_limit : "0",
			  file_post_name : "file", 				// FOR AWS

  			// Button settings
  			button_image_url : "/static/img/bug_big.png",
  			button_placeholder_id : "spanButtonPlaceHolder",
  			button_width: 61,
  			button_height: 22,
    
        // Flash Settings
        flash_url : "http://piles-dev.s3.amazonaws.com/swfupload.swf",
			  debug: true,
			  post_params: {
                  key:'{{key}}',
                  AWSAccessKeyId:'0Z67F08VD9JMM1WKRDR2',
                  acl:"private",
                  policy:'{{policy}}' ,//encodeURIComponent('{{policy}}'),
                  signature:'{{signature}}' //encodeURIComponent('{{signature}}'),
                  //success_action_status:201,
                }	// FOR AWS
 
    }) 
        .bind('swfuploadLoaded', function(event){
    			$('#log').append('<li>Loaded</li>');
    		})
    		.bind('fileQueued', function(event, file){
    			$('#log').append('<li>File queued - '+file.name+'</li>');
    			// start the upload since it's queued
    			$(this).swfupload('startUpload');
    		})
    		.bind('fileQueueError', function(event, file, errorCode, message){
    			$('#log').append('<li>File queue error - '+message+'</li>');
    		})
    		.bind('fileDialogStart', function(event){
    			$('#log').append('<li>File dialog start</li>');
    		})
    		.bind('fileDialogComplete', function(event, numFilesSelected, numFilesQueued){
    			$('#log').append('<li>File dialog complete</li>');
    		})
    		.bind('uploadStart', function(event, file){
    			$('#log').append('<li>Upload start - '+file.name+'</li>');
    		})
    		.bind('uploadProgress', function(event, file, bytesLoaded){
    			$('#log').append('<li>Upload progress - '+bytesLoaded+'</li>');
    		})
    		.bind('uploadSuccess', function(event, file, serverData){
    			$('#log').append('<li>Upload success - '+file.name+'</li>');
                alert('Holler!')
    		})
    		.bind('uploadComplete', function(event, file){
    			$('#log').append('<li>Upload complete - '+file.name+'</li>');
    			 
    			// Change this callback function to suite your needs
    			
    			// upload has completed, lets try the next one in the queue
    			$(this).swfupload('startUpload');
    		})
    		.bind('uploadError', function(event, file, errorCode, message){
    			$('#log').append('<li>Upload error - '+message+'</li>');
    		});
    
});
</script>

<div id="swfupload-control">
    <ol id="log"></ol>
    <span id="spanButtonPlaceHolder"></span>
</div>
%end

%rebase layout content=content, head=head, meta={'title':'S3 Test'}
Dropzone.autoDiscover = false;

const myDropzone = new Dropzone("#drag-drop-area", {
    url: "/upload-chunk/", 
    paramName: "file", 
    chunking: true,
    forceChunking: true,
    chunkSize: 5000000, 
    parallelChunkUploads: false, 
    retryChunks: true,
    maxFiles: 1,
    acceptedFiles: "video/*",
    
    headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
    },

    success: function(file, response) {
        const fileGuid = response.guid;
        const hiddenInput = document.querySelector('input[type="hidden"][id^="id_"]');
        
        if (hiddenInput) {
            hiddenInput.value = fileGuid;
            console.log("Upload concluído! GUID salvo:", fileGuid);
        }
    }
});
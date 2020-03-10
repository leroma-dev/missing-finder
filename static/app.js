var extract_data = {
    file: null
};

var train_data = {
    hash: "",
    file: null
};

var recognize_data = {
    file: null,
    id: null
};


var message = null;
var active_section = null;

function render(){

   // clear form data

   $('.form-item input').val('');
   $('.tabs li').removeClass('active');
   $('.tabs li:first').addClass('active');


   active_section = 'extract-content';

    $('#'+active_section).show();


}
function update(){


    if(message){
        // render message

        $('.message').html('<p class="'+_.get(message, 'type')+'">'+_.get(message, 'message')+'</p>');
    }else{
        $('.message').html('');
    }

    $('#extract-content, #train-content, #recognize-content').hide();
    $('#'+active_section).show();



}


$(document).ready(function(){




    // listen for file added

    $('#train #input-file').on('change', function(event){



        //set file object to train_data
        train_data.file = _.get(event, 'target.files[0]', null);


    });

    // listen for file added

    $('#extract #extract-file').on('change', function(event){



        //set file object to train_data
        extract_data.file = _.get(event, 'target.files[0]', null);


    });


    // listen for name change
    $('#hash-field').on('change', function(event){

        train_data.hash = _.get(event, 'target.value', '');

    });

    // listen tab item click on

    $('.tabs li').on('click', function(e){

        var $this = $(this);


        active_section = $this.data('section');

        // remove all active class

        $('.tabs li').removeClass('active');

        $this.addClass('active');

        message = null;

        update();



    });


    // listen the form train submit

    $('#train').submit(function(event){

        message = null;

        if(train_data.hash && train_data.file){
            // do send data to backend api

            var train_form_data = new FormData();

            train_form_data.append('hash', train_data.hash);
            train_form_data.append('file', train_data.file);

            axios.post('/api/train', train_form_data).then(function(response){

                message = {type: 'success', message: 'Treinamento feito'};

                train_data = {hash: '', file: null};
                update();

            }).catch(function(error){


                  message = {type: 'error', message: _.get(error, 'response.data.error.message', 'Unknown error.')}

                  update();
            });

        }else{

            message = {type: "error", message: "Hash e imagem da face necessários."}



        }

        update();
        event.preventDefault();
    });


    // listen for recognize file field change
    $('#recognize-input-file').on('change', function(e){


        recognize_data.file = _.get(e, 'target.files[0]', null);

    });

    // listen for id change
    $('#id-field').on('change', function(event){

        recognize_data.id = _.get(event, 'target.value', '');

    });
    // listen for recognition form submit
    $('#recognize').submit(function(e){



        // call to backend
        var recog_form_data = new FormData();
        recog_form_data.append('file', recognize_data.file);
        recog_form_data.append('id', recognize_data.id);

        axios.post('/api/recognize', recog_form_data).then(function(response){


            console.log("We found a user matched with your face image is", response.data);

            message = {type: 'success', message: 'Encontramos uma correspondência com a face: '+ response.data.path};

            recognize_data = {file: null, id: null};
            update();

        }).catch(function(err){


            message = {type: 'error', message: _.get(err, 'response.data.error.message', 'Unknown error')};

            update();

        });
        e.preventDefault();
    });

    // listen for recognition form submit
    $('#extract').submit(function(e){



        // call to backend
        var extract_form_data = new FormData();
        extract_form_data.append('file', extract_data.file);

        axios.post('/api/extract', extract_form_data).then(function(response){


            console.log("Number of faces found on image is", response.data);

            message = {type: 'success', message: 'Número de faces encontradas na imagem: '+ response.data.number};

            extract_data = {file: null};
            update();

        }).catch(function(err){


            message = {type: 'error', message: _.get(err, 'response.data.error.message', 'Unknown error')};

            update();

        });
        e.preventDefault();
    });


// render the app;
render();

});




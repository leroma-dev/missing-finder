var train_data = {
    id: 0,
    name: "",
    age: 0,
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


   active_section = 'train-content';

    $('#'+active_section).show();


}
function update(){


    if(message){
        // render message

        $('.message').html('<p class="'+_.get(message, 'type')+'">'+_.get(message, 'message')+'</p>');
    }else{
        $('.message').html('');
    }

    $('#train-content, #recognize-content').hide();
    $('#'+active_section).show();



}


$(document).ready(function(){




    // listen for file added

    $('#train #input-file').on('change', function(event){



        //set file object to train_data
        train_data.file = _.get(event, 'target.files[0]', null);


    });

    //
    // // listen for name change
    // $('#hash-field').on('change', function(event){
    //
    //     train_data.hash = _.get(event, 'target.value', '');
    //
    // });
    // listen for id change
    $('#id-field').on('change', function(event){

        train_data.id = _.get(event, 'target.value', '');

    });
    // listen for name change
    $('#name-field').on('change', function(event){

        train_data.name = _.get(event, 'target.value', '');

    });
    // listen for age change
    $('#age-field').on('change', function(event){

        train_data.age = _.get(event, 'target.value', '');

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

    $('#train').submit(function(e){

        message = null;

        if(train_data.id && train_data.name && train_data.age && train_data.file){
        // if(train_data.hash && train_data.file){
            // do send data to backend api

            var train_form_data = new FormData();

            // train_form_data.append('hash', train_data.hash);
            train_form_data.append('id', train_data.id);
            train_form_data.append('name', train_data.name);
            train_form_data.append('age', train_data.age);
            train_form_data.append('file', train_data.file);

            axios.post('/api/train', train_form_data).then(function(response){

                message = {type: 'success', message: 'Pessoa cadastrada'};

                // train_data = {hash: '', file: null};
                train_data = {id: 0, name: "", age: 0, file: null};
                update();

            }).catch(function(error){


                  message = {type: 'error', message: _.get(error, 'response.data.error.message', 'Unknown error.')}

                  update();
            });

        }else{

            message = {type: "error", message: "Por favor informe todos os dados."}


            update();
        }


        e.preventDefault();
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

    // render the app;
    render();

});




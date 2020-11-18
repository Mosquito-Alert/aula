var utils = (function(){
    var letters_up = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];
    var letters_lo = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'];
    var numbers = [0,1,2,3,4,5,6,7,8,9];

    return{
        generate_random_password_4: function(){
            var from = [letters_up,letters_lo,numbers];
            var pwd = [];
            for(var i = 0; i < 4; i++){
                var bag_n = from[Math.floor(Math.random() * 3)];
                pwd.push( bag_n[ Math.floor(Math.random() * bag_n.length ) ] );
            }
            return pwd.join('');
        },
        string_to_slug: function(str){
            str = str.replace(/^\s+|\s+$/g, ''); // trim
            str = str.toLowerCase();
            var from = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;";
            var to   = "aaaaeeeeiiiioooouuuunc------";
            for (var i=0, l=from.length ; i<l ; i++) {
                str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
            }
            str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
                .replace(/\s+/g, '-') // collapse whitespace and replace by -
                .replace(/-+/g, '-'); // collapse dashes

            return str;
        }
    }
})();
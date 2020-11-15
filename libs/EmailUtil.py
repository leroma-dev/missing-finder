class EmailUtil:
    def get_new_password_template(self, new_password):
        return """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <meta http-equiv="x-ua-compatible" content="ie=edge">
            <title>Nova senha</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style type="text/css">
                /**
            * Google webfonts. Recommended to include the .woff version for cross-client compatibility.
            */
                @media screen {
                @font-face {
                    font-family: 'Source Sans Pro';
                    font-style: normal;
                    font-weight: 400;
                    src: local('Source Sans Pro Regular'), local('SourceSansPro-Regular'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/ODelI1aHBYDBqgeIAH2zlBM0YzuT7MdOe03otPbuUS0.woff) format('woff');
                }

                @font-face {
                    font-family: 'Source Sans Pro';
                    font-style: normal;
                    font-weight: 700;
                    src: local('Source Sans Pro Bold'), local('SourceSansPro-Bold'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/toadOcfmlt9b38dHJxOBGFkQc6VGVFSmCnC_l7QZG60.woff) format('woff');
                }
                }

                /**
            * Avoid browser level font resizing.
            * 1. Windows Mobile
            * 2. iOS / OSX
            */
                body,
                table,
                td,
                a {
                -ms-text-size-adjust: 100%;
                /* 1 */
                -webkit-text-size-adjust: 100%;
                /* 2 */
                }

                /**
            * Remove extra space added to tables and cells in Outlook.
            */
                table,
                td {
                mso-table-rspace: 0pt;
                mso-table-lspace: 0pt;
                }

                /**
            * Better fluid images in Internet Explorer.
            */
                img {
                -ms-interpolation-mode: bicubic;
                }

                /**
            * Remove blue links for iOS devices.
            */
                a[x-apple-data-detectors] {
                font-family: inherit !important;
                font-size: inherit !important;
                font-weight: inherit !important;
                line-height: inherit !important;
                color: inherit !important;
                text-decoration: none !important;
                }

                /**
            * Fix centering issues in Android 4.4.
            */
                div[style*="margin: 16px 0;"] {
                margin: 0 !important;
                }

                body {
                width: 100% !important;
                height: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
                }

                /**
            * Collapse table borders to avoid space between cells.
            */
                table {
                border-collapse: collapse !important;
                }

                a {
                color: #1a82e2;
                }

                img {
                height: auto;
                line-height: 100%;
                text-decoration: none;
                border: 0;
                outline: none;
                }
            </style>
            </head>

            <body style="background-color: #e9ecef;">
            <!-- start preheader -->
            <div class="preheader"
                style="display: none; max-width: 0; max-height: 0; overflow: hidden; font-size: 1px; line-height: 1px; color: #fff; opacity: 0;">
                Uma nova senha temporária foi gerada para sua conta.
            </div>
            <!-- end preheader -->
            
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="center" valign="top" style="padding: 36px 24px;"></td>
            </tr>
            </table>

            <!-- start body -->
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <!-- start hero -->
                <tr>
                <td align="center" bgcolor="#e9ecef">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                    <tr>
                        <td align="left" bgcolor="#ffffff"
                        style="padding: 36px 24px 0; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; border-top: 3px solid #d4dadf;">
                        <h1 style="margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;">Sua
                            nova senha:</h1>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
                <!-- end hero -->

                <!-- start copy block -->
                <tr>
                <td align="center" bgcolor="#e9ecef">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">

                    <!-- start copy -->
                    <tr>
                        <td align="left" bgcolor="#ffffff"
                        style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
                        <p style="margin: 0;">Use a senha gerada abaixo para entrar em sua conta e, em seguida, altere-a para a
                            senha que desejar.</p>
                        </td>
                    </tr>
                    <!-- end copy -->

                    <!-- start button -->
                    <tr>
                        <td align="left" bgcolor="#ffffff">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                            <td align="center" bgcolor="#ffffff" style="padding: 12px;">
                                <table border="0" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" bgcolor="#fff0b3" style="border-radius: 6px;">
                                    <div
                                        style="display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; text-decoration: none; border-radius: 6px;">
                                        <b>""" + new_password + """</b></div>
                                    </td>
                                </tr>
                                </table>
                            </td>
                            </tr>
                        </table>
                        </td>
                    </tr>
                    <!-- end button -->

                    <!-- start copy -->
                    <tr>
                        <td align="left" bgcolor="#ffffff"
                        style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
                        <p style="margin: 0;">Caso a senha não funcione, entre em contato com a nossa equipe.</p>
                        </td>
                    </tr>
                    <!-- end copy -->

                    <!-- start copy -->
                    <tr>
                        <td align="left" bgcolor="#ffffff"
                        style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px; border-bottom: 3px solid #d4dadf">
                        <p style="margin: 0;">Atenciosamente,<br> Equipe Missing Finder.</p>
                        </td>
                    </tr>
                    <!-- end copy -->

                    </table>
                </td>
                </tr>
                <!-- end copy block -->

                <!-- start footer -->
                <tr>
                <td align="center" bgcolor="#e9ecef" style="padding: 24px;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">

                    <!-- start permission -->
                    <tr>
                        <td align="center" bgcolor="#e9ecef"
                        style="padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;">
                        <p style="margin: 0;">Você recebeu essa e-mail pois recebemos uma requisição de recuperação de senha para
                            sua conta. Caso não tenha sido você, entre em sua conta com a senha temporária e gere uma nova senha.
                        </p>
                        </td>
                    </tr>
                    <!-- end permission -->

                    <!-- start unsubscribe -->
                    <tr>
                        <td align="center" bgcolor="#e9ecef"
                        style="padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;">
                        <p style="margin: 0;">Missing Finder®</p>
                        </td>
                    </tr>
                    <!-- end unsubscribe -->

                    </table>
                </td>
                </tr>
                <!-- end footer -->

            </table>
            <!-- end body -->
            </body>
            </html>
        """

    def get_detected_person_template(self, person_name, reporter_name, reporter_email, reporter_phone):
        return """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <meta http-equiv="x-ua-compatible" content="ie=edge">
            <title>Nova senha</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style type="text/css">
                /**
            * Google webfonts. Recommended to include the .woff version for cross-client compatibility.
            */
                @media screen {
                @font-face {
                    font-family: 'Source Sans Pro';
                    font-style: normal;
                    font-weight: 400;
                    src: local('Source Sans Pro Regular'), local('SourceSansPro-Regular'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/ODelI1aHBYDBqgeIAH2zlBM0YzuT7MdOe03otPbuUS0.woff) format('woff');
                }

                @font-face {
                    font-family: 'Source Sans Pro';
                    font-style: normal;
                    font-weight: 700;
                    src: local('Source Sans Pro Bold'), local('SourceSansPro-Bold'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/toadOcfmlt9b38dHJxOBGFkQc6VGVFSmCnC_l7QZG60.woff) format('woff');
                }
                }

                /**
            * Avoid browser level font resizing.
            * 1. Windows Mobile
            * 2. iOS / OSX
            */
                body,
                table,
                td,
                a {
                -ms-text-size-adjust: 100%;
                /* 1 */
                -webkit-text-size-adjust: 100%;
                /* 2 */
                }

                /**
            * Remove extra space added to tables and cells in Outlook.
            */
                table,
                td {
                mso-table-rspace: 0pt;
                mso-table-lspace: 0pt;
                }

                /**
            * Better fluid images in Internet Explorer.
            */
                img {
                -ms-interpolation-mode: bicubic;
                }

                /**
            * Remove blue links for iOS devices.
            */
                a[x-apple-data-detectors] {
                font-family: inherit !important;
                font-size: inherit !important;
                font-weight: inherit !important;
                line-height: inherit !important;
                color: inherit !important;
                text-decoration: none !important;
                }

                /**
            * Fix centering issues in Android 4.4.
            */
                div[style*="margin: 16px 0;"] {
                margin: 0 !important;
                }

                body {
                width: 100% !important;
                height: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
                }

                /**
            * Collapse table borders to avoid space between cells.
            */
                table {
                border-collapse: collapse !important;
                }

                a {
                color: #1a82e2;
                }

                img {
                height: auto;
                line-height: 100%;
                text-decoration: none;
                border: 0;
                outline: none;
                }
            </style>
            </head>

            <body style="background-color: #e9ecef;">
            <!-- start preheader -->
            <div class="preheader"
                style="display: none; max-width: 0; max-height: 0; overflow: hidden; font-size: 1px; line-height: 1px; color: #fff; opacity: 0;">
                Um usuário encontrou a pessoa reportada por você.
            </div>
            <!-- end preheader -->
            
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="center" valign="top" style="padding: 36px 24px;"></td>
            </tr>
            </table>

            <!-- start body -->
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <!-- start hero -->
                <tr>
                <td align="center" bgcolor="#e9ecef">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                    <tr>
                        <td align="left" bgcolor="#ffffff"
                        style="padding: 36px 24px 0; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; border-top: 3px solid #d4dadf;">
                        <h1 style="margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;">Informações para contato:</h1>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
                <!-- end hero -->

                <!-- start copy block -->
                <tr>
                <td align="center" bgcolor="#e9ecef">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">

                    <!-- start copy -->
                    <tr>
                        <td align="left" bgcolor="#ffffff"
                        style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
                        <p style="margin: 0;">Um usuário assinalou ter encontrado <b>""" + person_name + """</b>. Para entrar em contato, utilize as informações abaixo.</p>
                        </td>
                    </tr>
                    <!-- end copy -->

                    <!-- start button -->
                    <tr>
                        <td align="left" bgcolor="#ffffff">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                            <td align="center" bgcolor="#ffffff" style="padding: 12px;">
                                <table border="0" cellpadding="8px" cellspacing="0">
                                <tr>
                                    <td>NOME:</td>
                                    <td align="center" bgcolor="#fff0b3" style="border-radius: 6px;">
                                    <div
                                        style="display: inline-block; padding: 8px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; text-decoration: none; border-radius: 6px;">
                                        <b>""" + reporter_name + """</b></div>
                                    </td>
                                </tr>
                                <tr><td></td><td></td></tr>
                                <tr>
                                    <td>E-MAIL:</td>
                                    <td align="center" bgcolor="#fff0b3" style="border-radius: 6px;">
                                    <div
                                        style="display: inline-block; padding: 8px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; text-decoration: none; border-radius: 6px;">
                                        <b>""" + reporter_email + """</b></div>
                                    </td>
                                </tr>
                                <tr><td></td><td></td></tr>
                                <tr>
                                    <td>TELEFONE:</td>
                                    <td align="center" bgcolor="#fff0b3" style="border-radius: 6px;">
                                    <div
                                        style="display: inline-block; padding: 8px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; text-decoration: none; border-radius: 6px;">
                                        <b>""" + reporter_phone + """</b></div>
                                    </td>
                                </tr>
                                </table>
                            </td>
                            </tr>
                        </table>
                        </td>
                    </tr>
                    <!-- end button -->

                    <!-- start copy -->
                    <tr>
                        <td align="left" bgcolor="#ffffff"
                        style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
                        <p style="margin: 0;">Qualquer problema, entre em contato com a nossa equipe.</p>
                        </td>
                    </tr>
                    <!-- end copy -->

                    <!-- start copy -->
                    <tr>
                        <td align="left" bgcolor="#ffffff"
                        style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px; border-bottom: 3px solid #d4dadf">
                        <p style="margin: 0;">Atenciosamente,<br> Equipe Missing Finder.</p>
                        </td>
                    </tr>
                    <!-- end copy -->

                    </table>
                </td>
                </tr>
                <!-- end copy block -->

                <!-- start footer -->
                <tr>
                <td align="center" bgcolor="#e9ecef" style="padding: 24px;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">

                    <!-- start permission -->
                    <tr>
                        <td align="center" bgcolor="#e9ecef"
                        style="padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;">
                        <p style="margin: 0;">Você recebeu essa e-mail pois reportou alguém em nosso app.</p>
                        </td>
                    </tr>
                    <!-- end permission -->

                    <!-- start unsubscribe -->
                    <tr>
                        <td align="center" bgcolor="#e9ecef"
                        style="padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;">
                        <p style="margin: 0;">Missing Finder®</p>
                        </td>
                    </tr>
                    <!-- end unsubscribe -->

                    </table>
                </td>
                </tr>
                <!-- end footer -->

            </table>
            <!-- end body -->
            </body>
            </html>
        """

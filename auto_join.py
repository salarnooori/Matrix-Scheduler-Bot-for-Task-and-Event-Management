from opsdroid.skill import Skill
from opsdroid.matchers import match_event
from opsdroid.events import UserInvite, JoinRoom, Message

class AutoJoin(Skill):

    @match_event(UserInvite)
    async def user_invite(self, invite):
        print("__INVITE__")
        if isinstance(invite, UserInvite):
            await invite.respond(JoinRoom())
            
    @match_event(JoinRoom)
    async def welcome_message(self, join_event):
        print("__JOINED__")
        if isinstance(join_event, JoinRoom):
            Hello_str = "سلام من ربات برنامه ریز زمانی برای کار هایتان هستم.\n"
            Hello_str += "ممنونم که منو انتخاب کردین :)\n"
            Hello_str += '''
          ___
         /   \\
        | ^  ^|
        | \\_/ |
        \\_____/______    
        //           \\\\
       ||             \\\\      
       \\\\      ***   ***
        =====**  ** ** **
            **    ***   **
              **      **
                **  **
                  **
        '''
            await join_event.respond(Message(text=Hello_str))
            Help_str = "من میتونم برنامه ریزی های مختلفت رو برات نگه دارم و بهت نشون بدم.\nراهنما:\n"
            Help_str += "1- ایجاد برنامه زمانی جدید. این قابلیت وقتی انجام میشه که جمله شما شامل کلمانی از دست( یادم باشه) به همراه یک تاریخ و یک عملی که میخواین انجام بدین باشه.\n\n"
            Help_str += "2- من میتونم کار هایی که قبلا اضافه کردی رو لغو کنم. فقط کافیه جمله ات شامل کلماتی ازین دست باشه(لغو کن، کنسل کن و ...) و یک عمل توش معلوم شده باشه.\n\n"
            Help_str += "3- من می تونم زمان انجام یه کاری که قبلا تعریف کردی رو تغیر بدم فقط باید جمله ات شامل یه عمل مد نظرت(میتونی تاریخشم خواستی بگی) به همراه تاریخ جدید و کلمه کلیدی (تغییر بده، عوض کن) رو داشته باشه.\n\n"
            Help_str += "4- وقتی یه کاری رو انجام میدی به من بگو تا وضعیتش رو تمام شده قرار بدم. برای این کار جمله ات باید شامل یه کار (اگه خواستی تاریخش رو هم بگو) به همراه کلمه کلید (انجام شد، تمام شد) باشه.\n\n"
            Help_str += "5- در نهایت اخرین کاری که فعلا توی این نسخه از من میتونی ببینی نمایش دادن لیست کار هاته. برای اینکار باید جمله ات شامل کلمه(نشان بده، نمایش بده، بگو) باشه و توی اون یه تاریخ یا یه زمان معلوم کن تا من لیست کارایی که توی اون تاریخ داری رو برات بگم."
            await join_event.respond(Message(text=Help_str))

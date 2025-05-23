from django.db import models

# Create your models here.

class BaseHashModel(models.Model):
    hash = models.TextField()  # النص المشفر باستخدام Argon2
    first_character = models.CharField(max_length=1, blank=True, null=True)
    second_character = models.CharField(max_length=1, blank=True, null=True)
    third_character = models.CharField(max_length=1, blank=True, null=True)
    fourth_character = models.CharField(max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.hash and len(self.hash) >= 4:  # التأكد من أن الـ hash ليس فارغًا وطوله على الأقل 4
            self.first_character = self.hash[0]
            self.second_character = self.hash[1]
            self.third_character = self.hash[2]
            self.fourth_character = self.hash[3]
        else:
            self.first_character = None
            self.second_character = None
            self.third_character = None
            self.fourth_character = None

        super().save(*args, **kwargs)  # حفظ البيانات في قاعدة البيانات

    class Meta:
        abstract = True  # جعل الكلاس كـ abstract حتى لا يتم إنشاؤه كجدول في قاعدة البيانات

        indexes = [
            models.Index(fields=['first_character', 'second_character']),
            models.Index(fields=['third_character', 'fourth_character']),
            models.Index(fields=['hash']),  # تحسين البحث باستخدام hash
        ]
    
class A(BaseHashModel):
    pass
   
class B(BaseHashModel):
    pass  

class C(BaseHashModel):
    pass
    
class D(BaseHashModel):
    pass

class E(BaseHashModel):
    pass

class F(BaseHashModel):
    pass

class G(BaseHashModel):
    pass

class H(BaseHashModel):
    pass

class I(BaseHashModel):
    pass

class J(BaseHashModel):
    pass

class K(BaseHashModel):
    pass

class L(BaseHashModel):
    pass

class M(BaseHashModel):
    pass
class N(BaseHashModel):
    pass

class O(BaseHashModel):
    pass

class P(BaseHashModel):
    pass

class Q(BaseHashModel):
    pass

class R(BaseHashModel):
    pass

class S(BaseHashModel):
    pass

class T(BaseHashModel):
    pass

class U(BaseHashModel):
    pass

class V(BaseHashModel):
    pass
    
class W(BaseHashModel):
    pass
    
class X(BaseHashModel):
    pass
    
class Y(BaseHashModel):
    pass
   
class Z(BaseHashModel):
    pass
    
########################################################################################################################

class Lowercase_a(BaseHashModel):
    pass

class Lowercase_b(BaseHashModel):
    pass

class Lowercase_c(BaseHashModel):
    pass 
    
class Lowercase_d(BaseHashModel):
    pass   

class Lowercase_e(BaseHashModel):
    pass

class Lowercase_f(BaseHashModel):
    pass
    
class Lowercase_g(BaseHashModel):
    pass
    
class Lowercase_h(BaseHashModel):
    pass
    
class Lowercase_i(BaseHashModel):
    pass
    
class Lowercase_j(BaseHashModel):
    pass
    
class Lowercase_k(BaseHashModel):
    pass
    
class Lowercase_l(BaseHashModel):
    pass
    
class Lowercase_m(BaseHashModel):
    pass
    
class Lowercase_n(BaseHashModel):
    pass
    
class Lowercase_o(BaseHashModel):
    pass
    
class Lowercase_p(BaseHashModel):
    pass
    
class Lowercase_q(BaseHashModel):
    pass
    
class Lowercase_r(BaseHashModel):
    pass
    
class Lowercase_s(BaseHashModel):
    pass
    
class Lowercase_t(BaseHashModel):
    pass
    
class Lowercase_u(BaseHashModel):
    pass
    
class Lowercase_v(BaseHashModel):
    pass
    
class Lowercase_w(BaseHashModel):
    pass
    
class Lowercase_x(BaseHashModel):
    pass
    
class Lowercase_y(BaseHashModel):
    pass
    
class Lowercase_z(BaseHashModel):
    pass
    
########################################################################################################################

class table_0(BaseHashModel):
    pass

class table_1(BaseHashModel):
    pass
    
class table_2(BaseHashModel):
    pass
    
class table_3(BaseHashModel):
    pass
    
class table_4(BaseHashModel):
    pass
    
class table_5(BaseHashModel):
    pass
    
class table_6(BaseHashModel):
    pass
    
class table_7(BaseHashModel):
    pass
    
class table_8(BaseHashModel):
    pass
    
class table_9(BaseHashModel):
    pass

########################################################################################################################

class SomthingElse(BaseHashModel):
    pass
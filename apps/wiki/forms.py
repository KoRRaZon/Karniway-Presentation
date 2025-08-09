from django import forms

from apps.wiki.models import Post, Creature, CreatureAttack, CreaturePassive


# Формы статей
class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']



# Формы существ

class CreatureForm(forms.ModelForm):

    class Meta:
        model = Creature
        fields = ['name', 'description', 'image',
                  'category', 'health', 'armor_class',
                  'speed', 'size', 'saving_throws',
                  'skills', 'dangerous_level', 'mastery',
                  'strength', 'dexterity', 'body_condition',
                  'intelligence', 'wisdom', 'charisma']


class CreatureAttackForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, initial='Рукопашная атака оружием: + к попаданию, досягаемость 5 футов, одна цель. Попадание: урона.')
    class Meta:
        model = CreatureAttack
        fields = ['name', 'text']


class CreaturePassiveForm(forms.ModelForm):
    class Meta:
        model = CreaturePassive
        fields = ['name', 'text']

# Inline formsets для удобного создания атак и особенностей существ.

CreatureAttackFormSet = forms.inlineformset_factory(
    parent_model=Creature,
    model=CreatureAttack,
    form=CreatureAttackForm,
    extra=1,
    can_delete=True,
    max_num=10,
    validate_max=True,
)

CreaturePassiveFormSet = forms.inlineformset_factory(
    parent_model=Creature,
    model=CreaturePassive,
    form=CreaturePassiveForm,
    extra=1,
    can_delete=True,
    max_num=10,
    validate_max=True,
)







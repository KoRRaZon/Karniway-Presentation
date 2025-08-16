from django import forms
from django.forms import inlineformset_factory

from apps.wiki.models import Post, Creature, CreatureAttack, CreaturePassive, Spell, SpellEffectLink


# Формы статей
class PostForm(forms.ModelForm):
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

# Формы заклинаний

class SpellForm(forms.ModelForm):
    class Meta:
        model = Spell
        fields = ('name', 'category', 'description', 'image', 'spell_level', 'requirements', 'special_components')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'requirements': forms.Textarea(attrs={'rows': 2}),
            'special_components': forms.Textarea(attrs={'rows': 2}),
        }


class SpellEffectLinkForm(forms.ModelForm):
    class Meta:
        model = SpellEffectLink
        fields = ['effect']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 6, 'style': 'resize: vertical'}),
        }


SpellEffectFormSet = inlineformset_factory(
    parent_model=Spell,
    model=SpellEffectLink,
    form=SpellEffectLinkForm,
    extra=1,
    can_delete=True,
    validate_max=False,
    validate_min=False,
)





